import http from 'node:http';

const port = Number(process.env.PORT || 10000);
const server = http.createServer((_request, response) => {
  response.writeHead(404, { 'content-type': 'application/json' });
  response.end('{"error":"not_found"}');
});

server.listen(port, '0.0.0.0', () => {
  console.log(`MIGRATION_RUNNER_READY port=${port}`);
});

function shutdown() {
  server.close(() => { process.exitCode = 0; });
}

process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);
