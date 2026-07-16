const http = require('http');
const fs = require('fs');

const BACKEND_PORT = parseInt(process.env.OPENCODE_BACKEND_PORT || '4097');
const PROXY_PORT = parseInt(process.env.OPENCODE_PROXY_PORT || '4096');
const CONFIG_PATH = process.env.OPENCODE_CONFIG_PATH || '/workspace/.config/opencode/opencode.json';

const AUTH = process.env.OPENCODE_SERVER_PASSWORD
  ? 'Basic ' + Buffer.from(process.env.OPENCODE_SERVER_USERNAME + ':' + process.env.OPENCODE_SERVER_PASSWORD).toString('base64')
  : null;

function backendFetch(path) {
  return new Promise(function(resolve, reject) {
    var opts = { hostname: '127.0.0.1', port: BACKEND_PORT, path: path, method: 'GET', headers: {} };
    if (AUTH) opts.headers.authorization = AUTH;
    var req = http.get(opts, function(res) {
      var d = '';
      res.on('data', function(c) { d += c; });
      res.on('end', function() { resolve(d); });
    });
    req.on('error', reject);
  });
}

function loadCustomAgents() {
  try {
    if (!fs.existsSync(CONFIG_PATH)) return [];
    var config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    var agents = config.agent || {};
    return Object.keys(agents).map(function(name) {
      return { name: name, description: agents[name].description || '', mode: agents[name].mode || 'subagent', native: false, permission: [], options: {} };
    });
  } catch (e) { return []; }
}

function loadCustomApiAgents() {
  try {
    if (!fs.existsSync(CONFIG_PATH)) return [];
    var config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    var agents = config.agent || {};
    return Object.keys(agents).map(function(name) {
      return { id: name, description: agents[name].description || '', mode: agents[name].mode || 'subagent', hidden: false, permissions: [], request: {}, system: '' };
    });
  } catch (e) { return []; }
}

var server = http.createServer(function(req, res) {
  var urlPath = req.url.split('?')[0];
  var isAgent = (urlPath === '/agent' || urlPath === '/api/agent') && req.method === 'GET';
  var isSkill = urlPath === '/api/skill' && req.method === 'GET';

  var opts = { hostname: '127.0.0.1', port: BACKEND_PORT, path: req.url, method: req.method, headers: {} };
  for (var k in req.headers) opts.headers[k] = req.headers[k];
  if (AUTH && !opts.headers.authorization) opts.headers.authorization = AUTH;

  var breq = http.request(opts, function(bres) {
    function passThrough() { res.writeHead(bres.statusCode, bres.headers); bres.pipe(res); }

    if ((isAgent || isSkill) && bres.statusCode === 200 && req.method === 'GET') {
      var body = '';
      bres.on('data', function(c) { body += c; });
      bres.on('end', function() {
        try {
          if (isSkill) {
            var orig = JSON.parse(body);
            var existing = orig.data || [];
            backendFetch('/skill?directory=/workspace').then(function(wsBody) {
              try {
                var wsSkills = JSON.parse(wsBody);
                var seen = {};
                existing.forEach(function(s) { seen[s.name] = true; });
                wsSkills.forEach(function(s) {
                  if (!seen[s.name]) { seen[s.name] = true; existing.push({ name: s.name, description: s.description || '', location: s.location || '', content: s.content || '' }); }
                });
                var merged = { location: orig.location, data: existing };
                res.writeHead(200, { 'content-type': 'application/json', 'access-control-allow-origin': '*' });
                res.end(JSON.stringify(merged));
              } catch (e) { passThrough(); }
            }, function() { passThrough(); });
          } else {
            var merged;
            if (urlPath === '/api/agent') {
              var orig = JSON.parse(body);
              merged = { location: orig.location, data: (orig.data || []).concat(loadCustomApiAgents()) };
            } else {
              merged = JSON.parse(body).concat(loadCustomAgents());
            }
            res.writeHead(200, { 'content-type': 'application/json', 'access-control-allow-origin': '*' });
            res.end(JSON.stringify(merged));
          }
        } catch (e) {
          console.error('[proxy] merge error:', e.message);
          passThrough();
        }
      });
    } else {
      passThrough();
    }
  });

  breq.on('error', function(e) {
    res.writeHead(502, { 'content-type': 'text/plain' });
    res.end('proxy error: ' + e.message);
  });

  req.pipe(breq);
});

server.on('error', function(e) {
  console.error('[proxy] FATAL:', e.message);
  process.exit(1);
});

server.listen(PROXY_PORT, '0.0.0.0', function() {
  console.log('[proxy] listening on :' + PROXY_PORT + ' -> :' + BACKEND_PORT);
});
