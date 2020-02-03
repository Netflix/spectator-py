import gzip
import io
import json
import logging
import time

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

    @staticmethod
    def _compress(entity):
        out = io.BytesIO()
        with gzip.GzipFile(fileobj=out, mode="w") as f:
            f.write(entity.encode('utf-8'))
        return out.getvalue()

    @staticmethod
    def _add_status_tags(tags, code):
        tags["statusCode"] = "{}".format(code)
        tags["status"] = "{}xx".format(int(code / 100))

    @staticmethod
    def _read_response(response):
        if response.info().get('Content-Encoding') == 'gzip':
            buf = io.BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            return f.read().decode()
        else:
            return response.read().decode()

    @staticmethod
    def _read_error(response):
        if response.headers.get('Content-Encoding', 'identity') == 'gzip':
            buf = io.BytesIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            return f.read().decode()
        else:
            return response.read().decode()

    def post_json(self, uri, data, retry_delay=3):
        max_attempts = 3

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

        attempt = 1

        while attempt <= max_attempts:
            try:
                response = urllib2.urlopen(request, timeout=self._timeout)
                self._add_status_tags(tags, response.code)
                msg = self._read_response(response)
                logger.debug("request succeeded, code=%d attempt=%d/%d: %s", response.code, attempt, max_attempts, msg)
                attempt = max_attempts + 1
            except urllib2.HTTPError as e:
                self._add_status_tags(tags, e.code)
                msg = self._read_error(e)
                logger.debug("request failed, code=%d attempt=%d/%d: %s", e.code, attempt, max_attempts, msg)
                if e.code == 429 or e.code >= 500:
                    time.sleep(retry_delay)
                    attempt += 1
                    if attempt > max_attempts:
                        logger.warning("request failed, max attempts exceeded: %s", msg)
                else:
                    logger.warning("request failed, code=%s not retryable: %s", e.code, msg)
                    attempt = max_attempts + 1
            except Exception as e:
                error = e.__class__.__name__
                tags["status"] = error
                tags["statusCode"] = error
                logger.warning("request failed, attempt=%d/%d, not retrying: %s", attempt, max_attempts, e)
                attempt = max_attempts + 1

        duration = self._registry.clock().monotonic_time() - start
        self._registry.timer("http.req.complete", tags).record(duration)
