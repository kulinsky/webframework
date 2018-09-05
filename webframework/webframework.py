import sys
import re
import traceback
from urllib.parse import parse_qs

from .databases.sqlworker import SQLWorker, SQLiteWorker


class Request:
    def __init__(self, environ):
        self.environ = environ
        self.path = environ["PATH_INFO"]
        self.method = environ['REQUEST_METHOD']
        self.headers = {k: v for k, v in environ.items() if k.startswith("HTTP_")}
        self.params = None
        self.GET = {k:v[0] for k,v in parse_qs(environ["QUERY_STRING"]).items()}
        self.POST = {}

        if self.method == "POST":
            try:
                content_length = int(environ.get("CONTENT_LENGTH", 0))
            except ValueError:
                content_length = 0

            qs = environ["wsgi.input"].read(content_length)
            self.POST = {k:v[0] for k,v in parse_qs(qs.decode()).items()}


class Response:
    def __init__(self, status='200 OK', body=b''):
        self.status = status
        self.body = body
        self.headers = {
            'Content-Type': 'text/html',
            'Content-Length': str(len(self.body))
        }

    @property
    def wsgi_headers(self):
        return [(k, v) for k, v in self.headers.items()]


class WebFramework:
    def __init__(self, sqlworker=None):
        self.routes = {}
        self._sqlworker = sqlworker or SQLiteWorker()

        if not isinstance(self._sqlworker, SQLWorker):
            raise ValueError('bad sqlworker instance', sqlworker)

    def __call__(self, environ, start_response):
        response = self.dispatch(Request(environ))
        start_response(response.status, response.wsgi_headers)
        return [response.body]

    def route(self, route_regex):
        def route_decorator(fn):
            self.routes[route_regex] = fn
            return fn
        return route_decorator

    @staticmethod
    def not_found():
        return Response(
            status="404 Not Found",
            body=b"Page not found."
        )

    @staticmethod
    def internal_error():
        return Response(
            status="500 Internal Server Error",
            body=b"An error has occurred."
        )

    def dispatch(self, request):
        for regex, view_func in self.routes.items():
            match = re.search(regex, request.path)
            if match is not None:
                request.params = match.groups()
                try:
                    return view_func(request)
                except Exception:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_tb(exc_traceback)
                    return self.internal_error()
        return self.not_found()

    def sql(self, query, params={}):
        return self._sqlworker.sql(query, params)
