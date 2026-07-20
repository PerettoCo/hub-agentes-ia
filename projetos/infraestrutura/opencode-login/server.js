const express = require('express');
const session = require('express-session');
const FileStore = require('session-file-store')(session);
const path = require('path');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const fs = require('fs');
const multer = require('multer');


const app = express();
app.set('trust proxy', 1);
const PORT = process.env.PORT || 3000;

const SESSION_SECRET = process.env.SESSION_SECRET;
const COOKIE_DOMAIN = process.env.COOKIE_DOMAIN || '.fvmarketing.com.br';
const PUBLIC_URL = process.env.PUBLIC_URL || 'https://ia.fvmarketing.com.br';
const SUPABASE_URL = process.env.SUPABASE_URL || '';
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY || '';
const USERS_PATH = process.env.USERS_PATH || '/data/users.json';
const BOOTSTRAP_ADMIN = process.env.BOOTSTRAP_ADMIN || '';
const DEFAULT_PASSWORD = process.env.DEFAULT_PASSWORD || 'v4@2025';
const USERDATA_PATH = process.env.USERDATA_PATH || '/user-data';

const TARGETS = {
  'marcos.luciano':     { redirect: 'https://ia.marcosluciano.fvmarketing.com.br' },
  'fhelipe.aranha':     { redirect: 'https://ia.fhelipearanha.fvmarketing.com.br' },
  'lucas.nunes':        { redirect: 'https://ia.lucasnunes.fvmarketing.com.br' },
  'paolo.carmine':      { redirect: 'https://ia.paolocarmine.fvmarketing.com.br' },
  'bruno.lindenmeyer':  { redirect: 'https://ia.brunolindenmeyer.fvmarketing.com.br' },
  'italo.rossi':        { redirect: 'https://ia.italorossi.fvmarketing.com.br' },
};

function userDir(username) { return username.replace(/\./g, '-'); }

function getTarget(username) {
  return TARGETS[username] || { redirect: PUBLIC_URL };
}

const DEFAULT_USERS = [
  { username: 'marcos.luciano',  name: 'Marcos Luciano', email: 'marcos@fvmarketing.com.br', squad: 'Growth', role: 'admin' },
  { username: 'fhelipe.aranha',  name: 'Fhelipe Aranha', email: 'fhelipe@fvmarketing.com.br', squad: 'Growth', role: 'user' },
  { username: 'lucas.nunes',     name: 'Lucas Nunes', email: 'lucas@fvmarketing.com.br', squad: 'Growth', role: 'user' },
  { username: 'paolo.carmine',   name: 'Paolo Carmine', email: 'paolo@fvmarketing.com.br', squad: 'Design', role: 'user' },
  { username: 'bruno.lindenmeyer', name: 'Bruno Lindenmeyer', email: 'bruno@fvmarketing.com.br', squad: 'Tech', role: 'user' },
  { username: 'italo.rossi',     name: 'Ítalo Rossi', email: 'italo@fvmarketing.com.br', squad: 'Design', role: 'user' },
];

function log(level, msg, meta) {
  const entry = { ts: new Date().toISOString(), level, service: 'auth', msg };
  if (meta) Object.assign(entry, meta);
  console.log(JSON.stringify(entry));
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    log('info', 'Created directory', { dir });
  }
}

function loadUsers() {
  try {
    ensureDir(path.dirname(USERS_PATH));
    if (fs.existsSync(USERS_PATH)) {
      const raw = fs.readFileSync(USERS_PATH, 'utf-8');
      const data = JSON.parse(raw);
      if (Array.isArray(data)) return data;
      if (data.users && Array.isArray(data.users)) return data.users;
    }
  } catch (e) {
    log('warn', 'Failed to load users file', { error: e.message });
  }
  return [];
}

function saveUsers(users) {
  try {
    ensureDir(path.dirname(USERS_PATH));
    fs.writeFileSync(USERS_PATH, JSON.stringify({ users }, null, 2), 'utf-8');
    log('info', 'Users saved', { count: users.length });
  } catch (e) {
    log('error', 'Failed to save users', { error: e.message });
  }
}

let users = [];

function applyPerUserPasswords() {
  let changed = false;
  for (const key of Object.keys(process.env)) {
    const match = key.match(/^USERPWD_(.+)$/);
    if (!match) continue;
    const username = match[1].replace(/_/g, '.');
    const user = users.find(u => u.username === username);
    if (user) {
      user.passwordHash = bcrypt.hashSync(process.env[key], 10);
      log('info', 'Applied per-user password', { username });
      changed = true;
    }
  }
  if (changed) saveUsers(users);
}

function loadOrSeedUsers() {
  const loaded = loadUsers();
  if (loaded.length > 0) {
    users = loaded;
    log('info', 'Loaded users from file', { count: users.length });
    applyPerUserPasswords();
    return;
  }

  log('info', 'Seeding default users');
  const hash = bcrypt.hashSync(DEFAULT_PASSWORD, 10);
  users = DEFAULT_USERS.map(u => ({ ...u, passwordHash: hash }));
  saveUsers(users);
  applyPerUserPasswords();

  if (BOOTSTRAP_ADMIN) {
    const [username] = BOOTSTRAP_ADMIN.split(':');
    if (!users.some(u => u.username === username)) {
      const hash = bcrypt.hashSync(DEFAULT_PASSWORD, 10);
      users.push({
        username,
        passwordHash: hash,
        name: username.split('.').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' '),
        email: `${username}@fvmarketing.com.br`,
        squad: 'Admin',
        role: 'admin',
      });
      saveUsers(users);
      log('info', 'Bootstrapped admin', { username });
    }
  }
}

function syncFromSupabase() {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) return;
  fetch(`${SUPABASE_URL}/rest/v1/users?select=*`, {
    headers: {
      'apikey': SUPABASE_SERVICE_KEY,
      'Authorization': `Bearer ${SUPABASE_SERVICE_KEY}`,
    },
  })
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(raw => {
      if (!raw || raw.length === 0) return;
      const supabaseUsers = raw.map(u => ({
        username: u.username,
        passwordHash: u.password_hash,
        name: u.name,
        email: u.email,
        squad: u.squad,
        role: u.role || 'user',
      }));

      const fileUsers = loadUsers();
      const merged = [...supabaseUsers];
      for (const fu of fileUsers) {
        const idx = merged.findIndex(u => u.username === fu.username);
        if (idx >= 0) {
          if (fu.role === 'admin') merged[idx] = fu;
        } else {
          merged.push(fu);
        }
      }
      users = merged;
      saveUsers(users);
      log('info', 'Synced from Supabase', { count: users.length });
    })
    .catch(e => log('warn', 'Supabase sync failed', { error: e.message }));
}

loadOrSeedUsers();
syncFromSupabase();
setInterval(syncFromSupabase, 5 * 60 * 1000);


const inputStorage = multer.diskStorage({
  destination: (req, file, cb) => {
    const dir = path.join(USERDATA_PATH, 'input', userDir(req.session.user.username));
    fs.mkdirSync(dir, { recursive: true });
    cb(null, dir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const ALLOWED_EXTENSIONS = new Set([
  '.pdf', '.doc', '.docx', '.odt', '.rtf',
  '.xls', '.xlsx', '.csv',
  '.ppt', '.pptx',
  '.txt', '.md', '.json', '.html', '.htm',
  '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp',
]);
const uploadInput = multer({
  storage: inputStorage,
  limits: { fileSize: 100 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const ext = path.extname(file.originalname).toLowerCase();
    if (!ALLOWED_EXTENSIONS.has(ext)) {
      return cb(new Error('Tipo de arquivo nao permitido: ' + ext));
    }
    cb(null, true);
  }
});




app.use(helmet({
  contentSecurityPolicy: false,
  crossOriginEmbedderPolicy: false,
}));

app.use(express.urlencoded({ extended: true }));
app.use(express.json());

ensureDir('/data/sessions');
app.use(session({
  store: new FileStore({ path: '/data/sessions', ttl: 86400 }),
  secret: SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    maxAge: 24 * 60 * 60 * 1000,
    httpOnly: true,
    sameSite: 'lax',
    domain: COOKIE_DOMAIN,
  },
}));

const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 20,
  message: { error: 'Muitas tentativas. Aguarde 15 minutos.' },
});

const apiLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 100,
  message: { error: 'Muitas requisições. Aguarde.' },
});

app.use('/static', express.static(path.join(__dirname, 'public'), { maxAge: '1h' }));

function requireAuth(req, res, next) {
  if (!req.session.user) return res.status(401).json({ error: 'Não autenticado' });
  next();
}

function requireAdmin(req, res, next) {
  if (!req.session.user) return res.status(401).json({ error: 'Não autenticado' });
  if (req.session.user.role !== 'admin') return res.status(403).json({ error: 'Acesso negado' });
  next();
}

app.get('/auth-check', (req, res) => {
  if (!req.session.user) return res.status(401).end();
  res.status(200).end();
});

app.get('/login', (req, res) => {
  if (req.session.user) return res.redirect('/');
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/login.html', (req, res) => res.redirect('/login'));

app.post('/login', loginLimiter, (req, res) => {
  const { username, password, redirect } = req.body;
  if (!username || !password) {
    return res.redirect('/login?error=' + encodeURIComponent('Preencha todos os campos'));
  }
  const user = users.find(u => u.username === username);
  if (!user) {
    return res.redirect('/login?error=' + encodeURIComponent('Credenciais inválidas'));
  }
  try {
    if (!bcrypt.compareSync(password, user.passwordHash)) {
      log('warn', 'Failed login attempt', { username });
      return res.redirect('/login?error=' + encodeURIComponent('Credenciais inválidas'));
    }
  } catch (e) {
    log('error', 'Bcrypt compare failed', { username, error: e.message });
    return res.redirect('/login?error=' + encodeURIComponent('Erro interno. Tente novamente.'));
  }
  req.session.user = {
    username: user.username,
    name: user.name,
    email: user.email,
    squad: user.squad,
    role: user.role || 'user',
  };
  req.session.save((err) => {
    if (err) log('error', 'Session save failed', { error: err.message });
    const dest = redirect || getTarget(user.username).redirect;
    log('info', 'User logged in', { username, role: user.role });
    res.redirect(dest);
  });
});

app.get('/api/me', requireAuth, (req, res) => {
  res.json(req.session.user);
});

app.get('/api/targets', requireAuth, (req, res) => {
  const target = getTarget(req.session.user.username);
  res.json({ targets: [
    { name: 'Hub de Agentes', url: target.redirect, icon: 'terminal' },
  ]});
});

app.post('/api/login', loginLimiter, (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Usuário e senha obrigatórios' });
  }
  const user = users.find(u => u.username === username);
  if (!user) return res.status(401).json({ error: 'Credenciais inválidas' });
  try {
    if (!bcrypt.compareSync(password, user.passwordHash)) {
      return res.status(401).json({ error: 'Credenciais inválidas' });
    }
  } catch (e) {
    return res.status(500).json({ error: 'Erro interno' });
  }
  req.session.user = {
    username: user.username,
    name: user.name,
    email: user.email,
    squad: user.squad,
    role: user.role || 'user',
  };
  req.session.save((err) => {
    if (err) return res.status(500).json({ error: 'Erro ao salvar sessão' });
    const target = getTarget(user.username);
    res.json({ success: true, user: req.session.user, redirectUrl: target.redirect });
  });
});

app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.clearCookie('connect.sid', { domain: COOKIE_DOMAIN, path: '/', secure: process.env.NODE_ENV === 'production', sameSite: 'lax' });
  res.json({ success: true });
});

app.get('/logout', (req, res) => {
  req.session.destroy();
  res.clearCookie('connect.sid', { domain: COOKIE_DOMAIN, path: '/', secure: process.env.NODE_ENV === 'production', sameSite: 'lax' });
  res.sendFile(path.join(__dirname, 'public', 'logout.html'));
});

app.get('/api/users', requireAdmin, (req, res) => {
  const safe = users.map(u => ({
    username: u.username,
    name: u.name,
    email: u.email,
    squad: u.squad,
    role: u.role || 'user',
  }));
  res.json(safe);
});

app.post('/api/users', requireAdmin, (req, res) => {
  const { username, name, email, squad, password, role } = req.body;
  if (!username || !name) {
    return res.status(400).json({ error: 'username e name são obrigatórios' });
  }
  if (users.some(u => u.username === username)) {
    return res.status(409).json({ error: 'Usuário já existe' });
  }
  const hash = password ? bcrypt.hashSync(password, 10) : bcrypt.hashSync(DEFAULT_PASSWORD, 10);
  const newUser = {
    username,
    name,
    email: email || `${username}@fvmarketing.com.br`,
    squad: squad || 'Geral',
    role: role || 'user',
    passwordHash: hash,
  };
  users.push(newUser);
  saveUsers(users);
  log('info', 'User created', { username, by: req.session.user.username });
  res.status(201).json({ success: true, user: { ...newUser, passwordHash: undefined } });
});

app.delete('/api/users/:username', requireAdmin, (req, res) => {
  const idx = users.findIndex(u => u.username === req.params.username);
  if (idx < 0) return res.status(404).json({ error: 'Usuário não encontrado' });
  if (users[idx].role === 'admin' && users.filter(u => u.role === 'admin').length <= 1) {
    return res.status(400).json({ error: 'Não pode remover o último admin' });
  }
  const removed = users.splice(idx, 1)[0];
  saveUsers(users);
  log('info', 'User removed', { username: removed.username, by: req.session.user.username });
  res.json({ success: true });
});

app.patch('/api/users/:username', requireAdmin, (req, res) => {
  const user = users.find(u => u.username === req.params.username);
  if (!user) return res.status(404).json({ error: 'Usuário não encontrado' });
  const { name, email, squad, role, password } = req.body;
  if (name !== undefined) user.name = name;
  if (email !== undefined) user.email = email;
  if (squad !== undefined) user.squad = squad;
  if (role !== undefined) user.role = role;
  if (password !== undefined) user.passwordHash = bcrypt.hashSync(password, 10);
  saveUsers(users);
  log('info', 'User updated', { username: user.username, by: req.session.user.username });
  res.json({ success: true, user: { ...user, passwordHash: undefined } });
});

app.get('/api/health', (req, res) => {
  res.json({
    status: 'healthy',
    uptime: process.uptime(),
    users: users.length,
    session: !!req.session?.user,
  });
});

app.get('/', (req, res) => {
  if (!req.session.user) return res.redirect('/login');
  res.sendFile(path.join(__dirname, 'public', 'dashboard.html'));
});

app.post('/api/upload', requireAuth, (req, res, next) => {
  uploadInput.single('file')(req, res, (err) => {
    if (err) return res.status(400).json({ error: 'Erro no upload: ' + err.message });
    if (!req.file) return res.status(400).json({ error: 'Nenhum arquivo enviado' });
    res.json({ success: true, file: { name: req.file.originalname, size: req.file.size, path: req.file.filename } });
  });
});

app.get('/api/files', requireAuth, (req, res) => {
  const dir = path.join(USERDATA_PATH, 'input', userDir(req.session.user.username));
  try {
    if (!fs.existsSync(dir)) return res.json([]);
    const files = fs.readdirSync(dir).map(f => {
      const stat = fs.statSync(path.join(dir, f));
      return { name: f, size: stat.size, modified: stat.mtime.toISOString() };
    });
    files.sort((a, b) => new Date(b.modified) - new Date(a.modified));
    res.json(files);
  } catch (e) { res.json([]); }
});

app.get('/api/files/:filename', requireAuth, (req, res) => {
  const filepath = path.join(USERDATA_PATH, 'input', userDir(req.session.user.username), req.params.filename);
  const resolved = path.resolve(filepath);
  if (!resolved.startsWith(path.resolve(USERDATA_PATH))) {
    return res.status(403).json({ error: 'Acesso negado' });
  }
  if (!fs.existsSync(resolved)) return res.status(404).json({ error: 'Arquivo nao encontrado' });
  res.download(resolved);
});

app.delete('/api/files/:filename', requireAuth, (req, res) => {
  const filepath = path.join(USERDATA_PATH, 'input', userDir(req.session.user.username), req.params.filename);
  const resolved = path.resolve(filepath);
  if (!resolved.startsWith(path.resolve(USERDATA_PATH))) {
    return res.status(403).json({ error: 'Acesso negado' });
  }
  if (!fs.existsSync(resolved)) return res.status(404).json({ error: 'Arquivo nao encontrado' });
  fs.unlinkSync(resolved);
  res.json({ success: true });
});

app.get('/api/outputs', requireAuth, (req, res) => {
  const dir = path.join(USERDATA_PATH, 'output', userDir(req.session.user.username));
  try {
    if (!fs.existsSync(dir)) return res.json([]);
    const items = [];
    (function walk(d, prefix) {
      const entries = fs.readdirSync(d, { withFileTypes: true });
      for (const e of entries) {
        const full = path.join(d, e.name);
        if (e.isDirectory()) { walk(full, prefix ? prefix + '/' + e.name : e.name); }
        else {
          const s = fs.statSync(full);
          items.push({ name: prefix ? prefix + '/' + e.name : e.name, size: s.size, modified: s.mtime.toISOString() });
        }
      }
    })(dir, '');
    items.sort((a, b) => new Date(b.modified) - new Date(a.modified));
    res.json(items);
  } catch (e) { res.json([]); }
});




app.use((err, req, res, next) => {
  log('error', 'Unhandled error', { error: err.message, stack: err.stack });
  res.status(500).json({ error: 'Erro interno do servidor' });
});

app.listen(PORT, () => {
  log('info', 'Auth server started', { port: PORT, domain: COOKIE_DOMAIN, users: users.length });
});
