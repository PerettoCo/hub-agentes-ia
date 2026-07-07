const express = require('express');
const session = require('express-session');
const path = require('path');
const fs = require('fs');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3000;

const SESSION_SECRET = process.env.SESSION_SECRET || 'CHAVE_SESSAO_32CARACTERES_AQUI';
const OPENCODE_HOST = process.env.OPENCODE_HOST || 'opencode-web';

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
    return user ? `http://${OPENCODE_HOST}:${user.opencodePort}` : null;
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
});

server.on('upgrade', (req, socket, head) => {
  const cookies = parseCookies(req.headers.cookie);
  const username = cookies.opencode_user;
  if (!username) { socket.destroy(); return; }
  const user = users.find(u => u.username === username);
  if (!user) { socket.destroy(); return; }
  const target = `http://${OPENCODE_HOST}:${user.opencodePort}`;
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
