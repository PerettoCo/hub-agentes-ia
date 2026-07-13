const express = require('express');
const session = require('express-session');
const path = require('path');
const fs = require('fs');
const bcrypt = require('bcryptjs');
const rateLimit = require('express-rate-limit');
const zlib = require('zlib');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
app.set('trust proxy', 1);
const PORT = process.env.PORT || 3000;

const SESSION_SECRET = process.env.SESSION_SECRET || 'CHAVE_SESSAO_32CARACTERES_AQUI';
const SUPABASE_URL = process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_KEY;
const OPENCODE_SERVER_USERNAME = process.env.OPENCODE_SERVER_USERNAME || 'opencode';
const OPENCODE_SERVER_PASSWORD = process.env.OPENCODE_SERVER_PASSWORD || '';
const BASIC_AUTH = Buffer.from(`${OPENCODE_SERVER_USERNAME}:${OPENCODE_SERVER_PASSWORD}`).toString('base64');

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
  if (req.session.user) {
    return res.send(`
      <!DOCTYPE html><html lang="pt-BR">
      <head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
      <title>V4 Company · Hub de Agentes</title>
      <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:Inter,system-ui,sans-serif;background:#0a0a0c;display:flex;align-items:center;justify-content:center;min-height:100vh;color:#fff}
        .card{background:#161618;border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:48px;text-align:center;max-width:400px}
        .avatar{width:64px;height:64px;border-radius:50%;background:#e63946;display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:700;margin:0 auto 16px}
        h2{font-size:1.2rem;font-weight:600;margin-bottom:4px}
        .sub{color:rgba(255,255,255,0.4);font-size:0.85rem;margin-bottom:24px}
        .btn{display:inline-block;padding:12px 32px;background:#e63946;color:#fff;border:none;border-radius:10px;font-size:0.9rem;font-weight:600;cursor:pointer;transition:background 0.2s;text-decoration:none}
        .btn:hover{background:#d32d3a}
        .btn-sec{background:transparent;border:1px solid rgba(255,255,255,0.1);color:rgba(255,255,255,0.6);margin-top:12px;display:inline-block;padding:10px 24px;border-radius:10px;font-size:0.82rem;cursor:pointer;text-decoration:none}
        .btn-sec:hover{border-color:rgba(255,255,255,0.2)}
        .flex{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
      </style></head>
      <body>
        <div class="card">
          <div class="avatar">${req.session.user.name.charAt(0).toUpperCase()}</div>
          <h2>${req.session.user.name}</h2>
          <div class="sub">${req.session.user.email || req.session.user.squad || req.session.user.username}</div>
          <div class="flex">
            <a href="/?directory=%2Fworkspace" class="btn">Acessar OpenCode</a>
            <form action="/api/logout" method="POST" style="display:inline">
              <button type="submit" class="btn-sec">Sair</button>
            </form>
          </div>
        </div>
      </body></html>
    `);
  }
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

app.get('/logout', (req, res) => {
  req.session.destroy();
  res.clearCookie('opencode_user');
  res.sendFile(path.join(__dirname, 'public', 'logout.html'));
});
app.post('/api/logout', (req, res) => {
  req.session.destroy();
  res.clearCookie('opencode_user');
  res.redirect('/logout');
});

app.use((req, res, next) => {
  if (!req.session.user) return res.redirect('/login');
  next();
});

const opencodeProxy = createProxyMiddleware({
  changeOrigin: true,
  proxyTimeout: 600000,
  timeout: 600000,
  router: (req) => {
    const user = users.find(u => u.username === req.session?.user?.username);
    const target = user ? `http://${user.opencodeHost}:${user.opencodePort}` : null;
    console.log(`[proxy] ${req.method} ${req.path} -> ${target || 'NO TARGET (null)'}`);
    return target;
  },
  on: {
    proxyReq: (proxyReq, req, res) => {
      if (BASIC_AUTH) proxyReq.setHeader('authorization', `Basic ${BASIC_AUTH}`);
    },
    proxyRes: (proxyRes, req, res) => {
      const ct = proxyRes.headers['content-type'] || '';
      console.log(`[proxy] ${req.method} ${req.path} <- ${proxyRes.statusCode} ${ct.substring(0,60)}`);
      if (!ct.includes('text/html')) return;

      proxyRes.pause();

      const enc = proxyRes.headers['content-encoding'];
      const chunks = [];
      proxyRes.on('data', chunk => chunks.push(chunk));
      proxyRes.on('end', () => {
        let buf = Buffer.concat(chunks);
        if (enc === 'gzip') buf = zlib.gunzipSync(buf);
        else if (enc === 'deflate') buf = zlib.inflateSync(buf);
        let body = buf.toString('utf-8');

        if (body.includes('</body>')) {
          const logoBase64 = fs.readFileSync(path.join(__dirname, 'public', 'logo-white.png')).toString('base64');
          const logoDataUri = `data:image/png;base64,${logoBase64}`;

          const inject = `
<style>
  [class*="logo"]:not([class*="icon"]):not([class*="badge"]),
  a[href*="opencode"] svg,
  header svg:first-child, nav svg:first-child {
    visibility: hidden !important;
    position: relative !important;
  }
  [class*="logo"]:not([class*="icon"]):not([class*="badge"])::after,
  a[href*="opencode"] svg::after,
  header svg:first-child::after, nav svg:first-child::after {
    content: '' !important;
    visibility: visible !important;
    position: absolute !important;
    top: 0; left: 0; width: 100%; height: 100%;
    background: url('${logoDataUri}') no-repeat center/contain !important;
  }
</style>
<script>
(function() {
  const LOGO = '${logoDataUri}';
  function replaceLogo() {
    var sel = 'a[href*="opencode"] svg,header svg,nav svg,[class*="logo"] svg';
    document.querySelectorAll(sel).forEach(function(el) {
      if (el.getAttribute('data-v4logo')) return;
      var img = document.createElement('img');
      img.src = LOGO;
      img.style.cssText = 'height:100%;width:auto;max-height:36px;';
      img.setAttribute('data-v4logo', '1');
      el.parentNode.replaceChild(img, el);
    });
  }
  document.addEventListener('DOMContentLoaded', replaceLogo);
  setTimeout(replaceLogo, 1000);
  setInterval(replaceLogo, 3000);
})();
</script>
<script>
(function() {
  var style = document.createElement('style');
  style.textContent = [
    '#v4-logout-btn{position:fixed;bottom:16px;right:16px;z-index:99999;background:rgba(230,57,70,0.9);color:#fff;border:none;border-radius:8px;padding:8px 16px;font-family:Inter,-apple-system,sans-serif;font-size:0.78rem;font-weight:600;cursor:pointer;transition:all 0.2s;box-shadow:0 4px 12px rgba(230,57,70,0.25);-webkit-font-smoothing:antialiased}',
    '#v4-logout-btn:hover{background:#d32d3a;transform:translateY(-1px);box-shadow:0 6px 20px rgba(230,57,70,0.35)}',
    '#v4-logout-btn:active{transform:translateY(0)}'
  ].join('');
  document.head.appendChild(style);
  var btn = document.createElement('button');
  btn.id = 'v4-logout-btn';
  btn.textContent = 'Sair';
  btn.title = 'Desconectar e trocar de usuário';
  btn.addEventListener('click', function() { window.location.href = '/logout'; });
  document.addEventListener('DOMContentLoaded', function() { document.body.appendChild(btn); });
  setTimeout(function() { if (!document.body.contains(btn)) document.body.appendChild(btn); }, 1000);
})();
</script>
</body>`;
          body = body.replace('</body>', inject);
        }

        delete proxyRes.headers['content-encoding'];
        const outBuf = Buffer.from(body, 'utf-8');
        proxyRes.headers['content-length'] = outBuf.length;
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        res.end(outBuf);
      });
    },
    error: (err, req, res) => {
      console.error('[proxy] ERROR:', err.message, req.method, req.path);
      if (res.writeHead) {
        res.writeHead(502, { 'Content-Type': 'text/plain' });
        res.end('Proxy error: OpenCode instance unavailable');
      }
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

const wsProxyInstance = createProxyMiddleware({
  changeOrigin: true,
  ws: true,
  router: (req) => {
    const cookies = parseCookies(req.headers.cookie);
    const username = cookies.opencode_user;
    if (!username) return null;
    const user = users.find(u => u.username === username);
    return user ? `http://${user.opencodeHost}:${user.opencodePort}` : null;
  }
});

server.on('upgrade', (req, socket, head) => {
  if (BASIC_AUTH) req.headers['authorization'] = `Basic ${BASIC_AUTH}`;
  wsProxyInstance.upgrade(req, socket, head);
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
