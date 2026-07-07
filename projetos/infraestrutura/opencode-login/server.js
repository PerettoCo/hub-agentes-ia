const express = require('express');
const session = require('express-session');
const path = require('path');
const fs = require('fs');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3000;

const SESSION_SECRET = process.env.SESSION_SECRET || 'CHAVE_SESSAO_32CARACTERES_AQUI';
const LITELLM_TARGET = process.env.LITELLM_TARGET || 'http://litellm:4000';
const OPENCODE_HOST = process.env.OPENCODE_HOST || 'opencode-web';
const PUBLIC_URL = process.env.PUBLIC_URL || '';

const usersPath = path.join(__dirname, 'users.json');
let users = [];
function loadUsers() {
  users = JSON.parse(fs.readFileSync(usersPath, 'utf-8')).users;
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

app.use(express.static(path.join(__dirname, 'public')));

function requireAuth(req, res, next) {
  if (req.session.user) return next();
  res.redirect('/login.html');
}

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
    squad: user.squad
  };
  res.json({ success: true, user: req.session.user });
});

app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.json({ success: true });
});

app.get('/api/targets', requireAuth, (req, res) => {
  const user = users.find(u => u.username === req.session.user.username);
  const baseUrl = PUBLIC_URL || `http://${OPENCODE_HOST}`;
  const targets = [
    {
      name: 'OpenCode Web',
      url: `${baseUrl}:${user.opencodePort}`,
      icon: 'terminal',
      description: 'Interface do agente de IA'
    },
    {
      name: 'LiteLLM Proxy',
      url: PUBLIC_URL ? `${PUBLIC_URL}:4000` : LITELLM_TARGET,
      icon: 'lightbulb',
      description: 'Proxy de modelos LLM'
    }
  ];
  res.json({ targets, user: req.session.user });
});

app.get('/dashboard', requireAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.get('/api/opencode-proxy', requireAuth, (req, res) => {
  const user = users.find(u => u.username === req.session.user.username);
  res.json({
    target: `http://${OPENCODE_HOST}:${user.opencodePort}`,
    user: req.session.user.username
  });
});

app.listen(PORT, () => {
  console.log(`[opencode-login] running on port ${PORT}`);
});
