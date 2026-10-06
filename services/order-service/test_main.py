import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from main import HealthHandler


class HealthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), HealthHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, method, path):
        connection = HTTPConnection(*self.server.server_address, timeout=3)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_health(self):
        status, headers, body = self.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(json.loads(body), {"status": "ok"})

    def test_head(self):
        status, _, body = self.request("HEAD", "/health")
        self.assertEqual(status, 200)
        self.assertEqual(body, b"")

    def test_unsupported_requests(self):
        for method, path, expected in [
            ("GET", "/", 404),
            ("GET", "/orders", 404),
            ("POST", "/orders", 404),
            ("GET", "/health/extra", 404),
            ("POST", "/health", 405),
        ]:
            with self.subTest(method=method, path=path):
                status, headers, _ = self.request(method, path)
                self.assertEqual(status, expected)
                if expected == 405:
                    self.assertEqual(headers["Allow"], "GET, HEAD")


if __name__ == "__main__":
    unittest.main()
