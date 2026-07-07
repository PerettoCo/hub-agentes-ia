const express = require('express');
const session = require('express-session');
const path = require('path');
const fs = require('fs');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
app.set('trust proxy', 1);
const PORT = process.env.PORT || 3000;

const SESSION_SECRET = process.env.SESSION_SECRET || 'CHAVE_SESSAO_32CARACTERES_AQUI';
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;

let users = [];
let usersLoaded = false;

async function loadUsers() {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    console.error('[opencode-login] SUPABASE_URL or SUPABASE_SERVICE_KEY not set');
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
      opencodeHost: u.opencode_host,
      opencodePort: u.opencode_port
    }));
    usersLoaded = true;
    console.log(`[opencode-login] Loaded ${users.length} users from Supabase`);
  } catch (e) {
    console.error('[opencode-login] Failed to load users from Supabase:', e.message);
  }
}

loadUsers();

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
    sameSite: 'lax'
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
    opencodeHost: user.opencodeHost,
    opencodePort: user.opencodePort
  };
  res.cookie('opencode_user', user.username, {
    httpOnly: true, sameSite: 'lax',
    maxAge: 24 * 60 * 60 * 1000
  });
  res.json({ success: true, user: req.session.user });
});

app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.clearCookie('opencode_user');
  res.json({ success: true });
});

app.use((req, res, next) => {
  if (!req.session.user) return res.redirect('/login');
  next();
});

const opencodeProxy = createProxyMiddleware({
  changeOrigin: true,
  ws: true,
  router: (req) => {
    const user = users.find(u => u.username === req.session?.user?.username);
    return user ? `http://${user.opencodeHost}:${user.opencodePort}` : null;
  },
  onError: (err, req, res) => {
    if (res.writeHead) {
      res.writeHead(502, { 'Content-Type': 'text/plain' });
      res.end('Proxy error: OpenCode instance unavailable');
    }
  }
});

app.use(opencodeProxy);

const server = app.listen(PORT, () => {
  console.log(`[opencode-login] running on port ${PORT}`);
  // Test connectivity to each OpenCode instance
  setTimeout(async () => {
    for (const u of users) {
      const target = `http://${u.opencodeHost}:${u.opencodePort}`;
      try {
        const ctrl = new AbortController();
        const t = setTimeout(() => ctrl.abort(), 5000);
        const r = await fetch(target, { signal: ctrl.signal });
        clearTimeout(t);
        console.log(`[opencode-login] ${u.username} -> ${target} = HTTP ${r.status}`);
      } catch (e) {
        console.log(`[opencode-login] ${u.username} -> ${target} = FAIL (${e.message})`);
      }
    }
  }, 3000);
});

server.on('upgrade', (req, socket, head) => {
  const cookies = parseCookies(req.headers.cookie);
  const username = cookies.opencode_user;
  if (!username) { socket.destroy(); return; }
  const user = users.find(u => u.username === username);
  if (!user) { socket.destroy(); return; }
  const target = `http://${user.opencodeHost}:${user.opencodePort}`;
  createProxyMiddleware({ target, changeOrigin: true, ws: true }).upgrade(req, socket, head);
});

function parseCookies(cookieHeader) {
  if (!cookieHeader) return {};
  return Object.fromEntries(
    cookieHeader.split(';').map(c => {
      const [k, ...v] = c.trim().split('=');
      return [k, decodeURIComponent(v.join('='))];
    })
  );
}
