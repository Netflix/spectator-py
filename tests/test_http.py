import gzip
import io
import json
import logging
import threading
import unittest

from spectator import Registry
from spectator.http import HttpClient

try:
    from BaseHTTPServer import HTTPServer
    from BaseHTTPServer import BaseHTTPRequestHandler
except ImportError:
    # python3
    from http.server import HTTPServer
    from http.server import BaseHTTPRequestHandler


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class HttpTest(unittest.TestCase):

    def setUp(self):
        self._server = HTTPServer(("localhost", 0), RequestHandler)
        self._uri = "http://localhost:{}/path".format(self._server.server_port)
        t = threading.Thread(target=self._server.serve_forever)
        t.start()

    def tearDown(self):
        self._server.shutdown()
        self._server.server_close()

    def test_do_post_ok(self):
        r = Registry()
        client = HttpClient(r)
        client.post_json(self._uri, '{"status": 200}', retry_delay=0)
        tags = {
            "mode": "http-client",
            "method": "POST",
            "client": "spectator-py",
            "status": "2xx",
            "statusCode": "200"
        }
        t = r.timer("http.req.complete", tags)
        self.assertEqual(t.count(), 1)

    def test_do_post_404(self):
        r = Registry()
        client = HttpClient(r)
        client.post_json(self._uri, '{"status": 404}', retry_delay=0)
        tags = {
            "mode": "http-client",
            "method": "POST",
            "client": "spectator-py",
            "status": "4xx",
            "statusCode": "404"
        }
        t = r.timer("http.req.complete", tags)
        self.assertEqual(t.count(), 1)

    def test_do_post_429(self):
        r = Registry()
        client = HttpClient(r)
        client.post_json(self._uri, '{"status": 429}', retry_delay=0)
        tags = {
            "mode": "http-client",
            "method": "POST",
            "client": "spectator-py",
            "status": "4xx",
            "statusCode": "429"
        }
        t = r.timer("http.req.complete", tags)
        self.assertEqual(t.count(), 1)

    def test_do_post_503(self):
        r = Registry()
        client = HttpClient(r)
        client.post_json(self._uri, '{"status": 503}', retry_delay=0)
        tags = {
            "mode": "http-client",
            "method": "POST",
            "client": "spectator-py",
            "status": "5xx",
            "statusCode": "503"
        }
        t = r.timer("http.req.complete", tags)
        self.assertEqual(t.count(), 1)

    def test_do_post_bad_json(self):
        r = Registry()
        client = HttpClient(r)
        client.post_json(self._uri, '{"status": ', retry_delay=0)
        tags = {
            "mode": "http-client",
            "method": "POST",
            "client": "spectator-py",
            "status": "4xx",
            "statusCode": "400"
        }
        t = r.timer("http.req.complete", tags)
        self.assertEqual(t.count(), 1)

    def test_do_post_encode(self):
        r = Registry()
        client = HttpClient(r)
        client.post_json(self._uri, {"status": 202}, retry_delay=0)
        tags = {
            "mode": "http-client",
            "method": "POST",
            "client": "spectator-py",
            "status": "2xx",
            "statusCode": "202"
        }
        t = r.timer("http.req.complete", tags)
        self.assertEqual(t.count(), 1)

    def test_do_post_network_error(self):
        self.tearDown()
        r = Registry()
        client = HttpClient(r)
        client.post_json(self._uri, "{}", retry_delay=0)
        tags = {
            "mode": "http-client",
            "method": "POST",
            "client": "spectator-py",
            "status": "URLError",
            "statusCode": "URLError"
        }
        t = r.timer("http.req.complete", tags)
        self.assertEqual(t.count(), 1)


class RequestHandler(BaseHTTPRequestHandler):

    @staticmethod
    def _compress(entity):
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(entity.encode('utf-8'))
        return out.getvalue()

    def do_POST(self):
        try:
            length = int(self.headers['Content-Length'])
            entity = io.BytesIO(self.rfile.read(length))
            data = json.loads(gzip.GzipFile(fileobj=entity).read().decode())
            self.send_response(data["status"])
            self.send_header('Content-Encoding', 'gzip')
            self.end_headers()
            self.wfile.write(self._compress("received: {}".format(data)))
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            msg = "error processing request: {}".format(e)
            self.wfile.write(msg.encode('utf-8'))

    def log_message(self, format, *args):
        pass
