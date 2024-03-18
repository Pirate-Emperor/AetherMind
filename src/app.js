const http = require('http');
const httpProxy = require('http-proxy');
const WebSocket = require('ws');

const proxy = httpProxy.createProxyServer({ target: 'http://0.0.0.0:8601' });

const server = http.createServer((req, res) => {
    proxy.web(req, res);
});

server.on('request', (req, res) => {
    console.log(`Received request for ${req.url} with method ${req.method}`);
});

server.on('upgrade', (req, socket, head) => {
    proxy.ws(req, socket, head);
});

proxy.on('close', (req, socket, head) => {
    console.log('Client disconnected');
});

proxy.on('error', (error, req, res) => {
    console.error('Proxy error:', error);
});

server.listen(8000);

// const wss = new WebSocket.Server({ server });

// wss.on('connection', (ws, req) => {
//     const target = new WebSocket(`ws://0.0.0.0:8501${req.url}`);
//     ws.on('message', message => target.send(message));
//     target.on('message', message => ws.send(message));
//     ws.on('close', () => target.close());
//     target.on('close', () => ws.close());
// });