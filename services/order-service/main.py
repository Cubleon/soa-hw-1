"""HTTP skeleton of the Orders service; no business operations."""

import signal
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


class HealthHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _respond(self):
        headers = {}
        if urlsplit(self.path).path != "/health":
            status, body = HTTPStatus.NOT_FOUND, b'{"error":"not found"}\n'
        elif self.command not in ("GET", "HEAD"):
            status = HTTPStatus.METHOD_NOT_ALLOWED
            body = b'{"error":"method not allowed"}\n'
            headers["Allow"] = "GET, HEAD"
        else:
            status, body = HTTPStatus.OK, b'{"status":"ok"}\n'

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.close_connection = True
        if self.command != "HEAD":
            self.wfile.write(body)

    do_GET = _respond
    do_HEAD = _respond
    do_POST = _respond
    do_PUT = _respond
    do_PATCH = _respond
    do_DELETE = _respond
    do_OPTIONS = _respond


def main():
    def stop(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGTERM, stop)
    with ThreadingHTTPServer(("0.0.0.0", 8080), HealthHandler) as server:
        print("order-service listening on 0.0.0.0:8080", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
