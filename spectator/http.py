import gzip
import io
import json
import logging
import sys

try:
    import urllib2
except ImportError:
    # python3 renames urllib2 to urllib.request
    import urllib.request as urllib2

logger = logging.getLogger("spectator.HttpClient")


class HttpClient:

    def __init__(self, registry, timeout=1):
        self._registry = registry
        self._timeout = timeout

    def _compress(self, entity):
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(entity.encode('utf-8'))
        return out.getvalue()

    def _add_status_tags(self, tags, code):
        tags["statusCode"] = "{}".format(code)
        tags["status"] = "{}xx".format(int(code / 100))

    def _read_response(self, response):
        if response.info().get('Content-Encoding') == 'gzip':
            buf = io.BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            return f.read()
        else:
            return response.read()

    def _read_error(self, response):
        if response.headers.get('Content-Encoding', 'identity') == 'gzip':
            buf = io.BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            return f.read()
        else:
            return response.read()

    def post_json(self, uri, data):
        headers = {
            "Accept-Encoding": "gzip",
            "Content-Encoding": "gzip",
            "Content-Type": "application/json"
        }

        tags = {
            "client": "spectator-py",
            "method": "POST",
            "mode": "http-client"
        }

        if type(data) is str:
            entity = data
        else:
            entity = json.dumps(data)

        logger.debug("posting data to %s, payload: %s", uri, entity)
        request = urllib2.Request(uri, self._compress(entity), headers)

        start = self._registry.clock().monotonic_time()
        try:
            response = urllib2.urlopen(request, timeout=self._timeout)
            self._add_status_tags(tags, response.code)
            msg = self._read_response(response)
            logger.debug("request succeeded (%d): %s", response.code, msg)
        except urllib2.HTTPError as e:
            self._add_status_tags(tags, e.code)
            msg = self._read_error(e)
            logger.warning("request failed (%d): %s", e.code, msg)
        except urllib2.URLError as e:
            error = type(e).__name__
            tags["status"] = error
            tags["statusCode"] = error
            logger.warning("request failed: %s", e)
        except:
            e = sys.exc_info()[0]
            error = type(e).__name__
            tags["status"] = error
            tags["statusCode"] = error
            logger.warning("request failed: %s", e)

        duration = self._registry.clock().monotonic_time() - start
        self._registry.timer("http.req.complete", tags).record(duration)
