const http = require('http');

const OPENCODE_HOST = process.env.OPENCODE_HOST || 'opencode-marcos';
const OPENCODE_PORT = parseInt(process.env.OPENCODE_PORT || '4096', 10);
const PORT = parseInt(process.env.PORT || '3000', 10);
const TARGET = `http://${OPENCODE_HOST}:${OPENCODE_PORT}`;

const BASIC_AUTH = Buffer.from(
  `${process.env.OPENCODE_SERVER_USERNAME || 'opencode'}:${process.env.OPENCODE_SERVER_PASSWORD || ''}`
).toString('base64');

console.log(`[opencode-proxy] ${TARGET}`);
console.log(`[opencode-proxy] basic-auth: ${!!BASIC_AUTH}`);

const server = http.createServer((req, res) => {
  console.log(`[proxy] ${req.method} ${req.url}`);

  const headers = { ...req.headers };
  headers.host = `${OPENCODE_HOST}:${OPENCODE_PORT}`;
  if (BASIC_AUTH) headers.authorization = `Basic ${BASIC_AUTH}`;
  headers.connection = 'keep-alive';
  delete headers['proxy-connection'];

  const proxyReq = http.request(
    {
      hostname: OPENCODE_HOST,
      port: OPENCODE_PORT,
      path: req.url,
      method: req.method,
      headers,
    },
    (proxyRes) => {
      const outHeaders = { ...proxyRes.headers };
      delete outHeaders['transfer-encoding'];
      if (proxyRes.headers['content-type']?.includes('text/event-stream')) {
        outHeaders['cache-control'] = 'no-cache';
        outHeaders['connection'] = 'keep-alive';
        outHeaders['x-accel-buffering'] = 'no';
        console.log(`[proxy] SSE stream ${req.url}`);
      }
      res.writeHead(proxyRes.statusCode, outHeaders);
      proxyRes.pipe(res);
    }
  );

  proxyReq.on('error', (err) => {
    console.error(`[proxy] ERROR ${req.url}: ${err.message}`);
    if (!res.headersSent) {
      res.writeHead(502, { 'Content-Type': 'text/plain' });
      res.end(`Proxy error: ${err.message}`);
    }
  });

  proxyReq.setTimeout(30000, () => {
    proxyReq.destroy(new Error('timeout'));
  });

  req.pipe(proxyReq);

  req.on('close', () => {
    if (!proxyReq.destroyed) proxyReq.destroy();
  });
});

server.on('upgrade', (req, socket, head) => {
  console.log(`[ws] ${req.url}`);

  const headers = { ...req.headers };
  headers.host = `${OPENCODE_HOST}:${OPENCODE_PORT}`;
  if (BASIC_AUTH) headers.authorization = `Basic ${BASIC_AUTH}`;

  const proxyReq = http.request({
    hostname: OPENCODE_HOST,
    port: OPENCODE_PORT,
    path: req.url,
    method: 'GET',
    headers,
  });

  proxyReq.on('upgrade', (proxyRes, proxySocket) => {
    socket.write(
      'HTTP/1.1 101 Switching Protocols\r\n' +
      'Upgrade: websocket\r\n' +
      'Connection: Upgrade\r\n' +
      '\r\n'
    );
    proxySocket.pipe(socket);
    socket.pipe(proxySocket);
  });

  proxyReq.on('error', (err) => {
    console.error(`[ws] ERROR ${req.url}: ${err.message}`);
    socket.destroy();
  });

  proxyReq.end();
});

server.listen(PORT, () => {
  console.log(`[opencode-proxy] listening on 0.0.0.0:${PORT}`);
});
