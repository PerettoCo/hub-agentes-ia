const express = require('express');
const session = require('express-session');
const path = require('path');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');

const app = express();
app.set('trust proxy', 1);
const PORT = process.env.PORT || 3000;

const SESSION_SECRET = process.env.SESSION_SECRET || 'CHAVE_SESSAO_32CARACTERES_AQUI';
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const COOKIE_DOMAIN = '.fvmarketing.com.br';

const PUBLIC_URL = process.env.PUBLIC_URL || 'https://ia.fvmarketing.com.br';

const SKILL_COUNT = 102;
const AGENT_COUNT = 36;
const TEAM_COUNT = 8;

const TARGETS = {
  'marcos.luciano': { redirect: 'https://marcos.fvmarketing.com.br' },
  'fhelipe.aranha': { redirect: 'https://fhelipe.fvmarketing.com.br' },
  'lucas.nunes': { redirect: 'https://lucasnunes.fvmarketing.com.br' },
  'csm1': { redirect: 'https://csm1.fvmarketing.com.br' },
};
const DEFAULT_TARGET = TARGETS['marcos.luciano'];

function getTarget(username) {
  return TARGETS[username] || DEFAULT_TARGET;
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

// ─── Auth-check (usado pelo nginx auth_request) ───
app.get('/auth-check', (req, res) => {
  if (!req.session.user) return res.status(401).end();
  res.status(200).end();
});

// ─── Login page ───
app.get('/login', (req, res) => {
  if (req.session.user) return res.redirect('/');
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});
app.get('/login.html', (req, res) => res.redirect('/login'));

// ─── Login via form POST (server-side redirect — mais robusto que fetch) ───
app.post('/login', loginLimiter, async (req, res) => {
  const { username, password, redirect } = req.body;
  if (!username || !password) {
    return res.redirect('/login?error=' + encodeURIComponent('Preencha todos os campos'));
  }
  const user = users.find(u => u.username === username);
  if (!user) {
    return res.redirect('/login?error=' + encodeURIComponent('Credenciais inválidas'));
  }
  const match = await bcrypt.compare(password, user.passwordHash);
  if (!match) {
    return res.redirect('/login?error=' + encodeURIComponent('Credenciais inválidas'));
  }
  req.session.user = {
    username: user.username,
    name: user.name,
    email: user.email,
    squad: user.squad,
  };
  req.session.save((err) => {
    if (err) console.error('[auth] session save error:', err);
    const dest = redirect || getTarget(user.username).redirect;
    res.redirect(dest);
  });
});

// ─── API: me ───
app.get('/api/me', (req, res) => {
  if (!req.session.user) return res.status(401).json({ error: 'not authenticated' });
  res.json(req.session.user);
});

// ─── API: targets ───
app.get('/api/targets', (req, res) => {
  if (!req.session.user) return res.status(401).json({ error: 'not authenticated' });
  const target = getTarget(req.session.user.username);
  res.json({
    targets: [
      { name: 'OpenCode Web', url: target.redirect, icon: 'terminal' },
    ]
  });
});

// ─── API: login ───
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
  req.session.save((err) => {
    if (err) console.error('[auth] session save error:', err);
    const target = getTarget(user.username);
    res.json({ success: true, user: req.session.user, redirectUrl: target.redirect });
  });
});

// ─── API: logout ───
const CLEAR_COOKIE = {
  domain: COOKIE_DOMAIN,
  path: '/',
  secure: process.env.NODE_ENV === 'production',
  sameSite: 'lax',
};

app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.clearCookie('connect.sid', CLEAR_COOKIE);
  res.json({ success: true });
});

app.get('/logout', (req, res) => {
  req.session.destroy();
  res.clearCookie('connect.sid', CLEAR_COOKIE);
  res.sendFile(path.join(__dirname, 'public', 'logout.html'));
});

// ─── Dashboard ───
app.get('/', (req, res) => {
  if (!req.session.user) return res.redirect('/login');
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.listen(PORT, () => {
  console.log(`[auth] listening on 0.0.0.0:${PORT}`);
  console.log(`[auth] cookie domain: ${COOKIE_DOMAIN}`);
});
