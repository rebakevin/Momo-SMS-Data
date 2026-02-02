import json
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from openapi.docs import DOC_ROUTES
from api.routes import ROUTES as APP_ROUTES
from api.service import SMSTransactionsService

# Merge routes from app and docs
ROUTES = {}
for source in [APP_ROUTES, DOC_ROUTES]:
    for method, paths in source.items():
        if method not in ROUTES:
            ROUTES[method] = {}
        ROUTES[method].update(paths)


class SMSTransactionsController(BaseHTTPRequestHandler):

    service = SMSTransactionsService()

    def __init__(self, *args, **kwargs):
        self.user_id = None
        self.route_params = {}
        super().__init__(*args, **kwargs)

    def log_request(self, code='-', size='-'):
        message = f"{self.command} {self.path} {code}"
        t_id = self.route_params.get('id')
        self.service.log_activity("HTTP", message, user_id=self.user_id, transaction_id=t_id)
        # super().log_request(code, size)

    def _match_route(self, method, path):
        routes = ROUTES.get(method, {})

        if path in routes:
            return routes[path], {}

        for route_pattern, handler in routes.items():
            if ':' in route_pattern:
                # Convert route pattern to regex
                # /transactions/:id -> /transactions/([^/]+)
                regex_pattern = re.sub(r':(\w+)', r'([^/]+)', route_pattern)
                regex_pattern = '^' + regex_pattern + '$'

                match = re.match(regex_pattern, path)
                if match:
                    # Extract parameter names and values
                    param_names = re.findall(r':(\w+)', route_pattern)
                    params = dict(zip(param_names, match.groups()))
                    return handler, params

        return None, {}

    def _send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')

        if status_code == 401:
            self.send_header('WWW-Authenticate', 'Basic realm="Momo API"')

        self.end_headers()
        response = {"error": message}
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path

        handler_func, params = self._match_route('GET', path)
        self.route_params = params
        if handler_func:
            if params:
                handler_func(self, **params)
            else:
                handler_func(self)
        else:
            self._send_error_response(404, "Route not found")

    def do_POST(self):
        path = urlparse(self.path).path

        handler_func, params = self._match_route('POST', path)
        self.route_params = params
        if handler_func:
            if params:
                handler_func(self, **params)
            else:
                handler_func(self)
        else:
            self._send_error_response(404, "Route not found")

    def do_PUT(self):
        path = urlparse(self.path).path

        handler_func, params = self._match_route('PUT', path)
        self.route_params = params
        if handler_func:
            if params:
                handler_func(self, **params)
            else:
                handler_func(self)
        else:
            self._send_error_response(404, "Route not found")

    def do_DELETE(self):
        path = urlparse(self.path).path

        handler_func, params = self._match_route('DELETE', path)
        self.route_params = params
        if handler_func:
            if params:
                handler_func(self, **params)
            else:
                handler_func(self)
        else:
            self._send_error_response(404, "Route not found")
