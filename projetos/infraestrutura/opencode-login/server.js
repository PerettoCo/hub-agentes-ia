const express = require('express');
const session = require('express-session');
const path = require('path');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
app.set('trust proxy', 1);
const PORT = process.env.PORT || 3000;

const SESSION_SECRET = process.env.SESSION_SECRET || 'CHAVE_SESSAO_32CARACTERES_AQUI';
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const OPENCODE_USERNAME = process.env.OPENCODE_SERVER_USERNAME || 'opencode';
const OPENCODE_PASSWORD = process.env.OPENCODE_SERVER_PASSWORD || '';
const COOKIE_DOMAIN = '.fvmarketing.com.br';

const AUTH_HEADER = 'Basic ' + Buffer.from(`${OPENCODE_USERNAME}:${OPENCODE_PASSWORD}`).toString('base64');

const PUBLIC_URL = process.env.PUBLIC_URL || 'https://ia.fvmarketing.com.br';

const HOST_MAP = {
  'marcos.fvmarketing.com.br': { upstream: 'http://opencode-marcos:4096', user: 'marcos.luciano' },
  'fhelipe.fvmarketing.com.br': { upstream: 'http://opencode-fhelipe:4096', user: 'fhelipe.aranha' },
  'lucasnunes.fvmarketing.com.br': { upstream: 'http://opencode-lucasnunes:4096', user: 'lucas.nunes' },
  'csm1.fvmarketing.com.br': { upstream: 'http://opencode-csm1:4096', user: 'csm1' },
};

const TARGETS = {};
for (const [host, cfg] of Object.entries(HOST_MAP)) {
  TARGETS[cfg.user] = { upstream: cfg.upstream, redirect: `https://${host}` };
}
const DEFAULT_TARGET = TARGETS['marcos.luciano'];

function getTarget(username) {
  return TARGETS[username] || DEFAULT_TARGET;
}

function getHostConfig(host) {
  if (!host) return null;
  return HOST_MAP[host.toLowerCase()] || null;
}

function isAuthHost(host) {
  if (!host) return true;
  const h = host.toLowerCase();
  return h === 'ia.fvmarketing.com.br' || !HOST_MAP[h];
}

let users = [];

async function loadUsers() {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('[auth] SUPABASE_URL or SUPABASE_SERVICE_KEY not set');
    return;
  }
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/users?select=*`, {
      headers: {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`
      }
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const raw = await res.json();
    users = raw.map(u => ({
      username: u.username,
      passwordHash: u.password_hash,
      name: u.name,
      email: u.email,
      squad: u.squad,
    }));
    console.log(`[auth] Loaded ${users.length} users from Supabase`);
  } catch (e) {
    console.error('[auth] Failed to load users:', e.message);
  }
}

loadUsers();
setInterval(loadUsers, 5 * 60 * 1000);

app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(session({
  secret: SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    maxAge: 24 * 60 * 60 * 1000,
    httpOnly: true,
    sameSite: 'lax',
    domain: COOKIE_DOMAIN,
  }
}));

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: { error: 'Muitas tentativas. Aguarde 15 minutos.' }
});

app.use('/static', express.static(path.join(__dirname, 'public')));

app.get('/login', (req, res) => {
  if (req.session.user) return res.redirect('/');
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});
app.get('/login.html', (req, res) => res.redirect('/login'));

app.get('/api/me', (req, res) => {
  if (!req.session.user) return res.status(401).json({ error: 'not authenticated' });
  res.json(req.session.user);
});

app.get('/api/targets', (req, res) => {
  if (!req.session.user) return res.status(401).json({ error: 'not authenticated' });
  const target = getTarget(req.session.user.username);
  res.json({
    targets: [
      { name: 'OpenCode Web', url: target.redirect, icon: 'terminal' },
    ]
  });
});

app.post('/api/login', loginLimiter, async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Usuário e senha obrigatórios' });
  }
  const user = users.find(u => u.username === username);
  if (!user) {
    return res.status(401).json({ error: 'Credenciais inválidas' });
  }
  const match = await bcrypt.compare(password, user.passwordHash);
  if (!match) {
    return res.status(401).json({ error: 'Credenciais inválidas' });
  }
  req.session.user = {
    username: user.username,
    name: user.name,
    email: user.email,
    squad: user.squad,
  };
  req.session.save();
  const target = getTarget(user.username);
  res.json({ success: true, user: req.session.user, redirectUrl: target.redirect });
});

app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

app.get('/logout', (req, res) => {
  req.session.destroy();
  res.sendFile(path.join(__dirname, 'public', 'logout.html'));
});

app.get('/', (req, res) => {
  const host = req.headers.host;
  if (isAuthHost(host)) {
    if (!req.session.user) return res.redirect('/login');
    return res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
  }
  if (!req.session.user) {
    return res.sendFile(path.join(__dirname, 'public', 'login.html'));
  }
  const config = getHostConfig(host);
  if (config && req.session.user.username !== config.user) {
    const target = getTarget(req.session.user.username);
    return res.redirect(target.redirect);
  }
  proxyRequest(req, res);
});

const opencodeProxy = createProxyMiddleware({
  changeOrigin: true,
  ws: true,
  router: (req) => {
    const config = getHostConfig(req.headers.host);
    return config ? config.upstream : null;
  },
  on: {
    proxyReq: (proxyReq, req) => {
      proxyReq.setHeader('Authorization', AUTH_HEADER);
    },
    error: (err, req, res) => {
      console.error('[proxy]', err.message);
      if (!res.headersSent) res.status(502).send('Upstream unavailable');
    },
  },
});

function proxyRequest(req, res) {
  const config = getHostConfig(req.headers.host);
  if (!config) {
    return res.redirect('https://ia.fvmarketing.com.br');
  }
  if (!req.session.user) {
    return res.sendFile(path.join(__dirname, 'public', 'login.html'));
  }
  opencodeProxy(req, res, (err) => {
    if (err) {
      console.error('[proxy] fallback error:', err.message);
      if (!res.headersSent) res.status(502).send('Proxy error');
    }
  });
}

app.use((req, res) => {
  proxyRequest(req, res);
});

const server = app.listen(PORT, () => {
  console.log(`[auth] listening on 0.0.0.0:${PORT}`);
  console.log(`[auth] cookie domain: ${COOKIE_DOMAIN}`);
  console.log(`[auth] proxy targets: ${Object.keys(HOST_MAP).join(', ')}`);
});

server.on('upgrade', (req, socket, head) => {
  const config = getHostConfig(req.headers.host);
  if (!config) {
    socket.destroy();
    return;
  }
  opencodeProxy.upgrade(req, socket, head);
});
