import json
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from openapi.docs import DOC_ROUTES
from api.routes import ROUTES as APP_ROUTES
from api.service import SMSTransactionsService

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
        
        log_type = "HTTP"
        if isinstance(code, int):
            if code >= 400:
                log_type = "HTTP_ERROR"
        elif isinstance(code, str) and (code.startswith('4') or code.startswith('5') or code == '-'):
             log_type = "HTTP_ERROR"

        self.service.log_activity(log_type, message, user_id=self.user_id, transaction_id=t_id)

    def log_error(self, format, *args):
        message = format % args
        self.service.log_activity("ERROR", f"Protocol Error: {message}", user_id=self.user_id)

    def _match_route(self, method, path):
        routes = ROUTES.get(method, {})

        if path in routes:
            return routes[path], {}

        for route_pattern, handler in routes.items():
            if ':' in route_pattern:
                regex_pattern = re.sub(r':(\w+)', r'([^/]+)', route_pattern)
                regex_pattern = '^' + regex_pattern + '$'

                match = re.match(regex_pattern, path)
                if match:
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
        try:
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
        except Exception as e:
            self.service.log_activity("EXCEPTION", f"Server Error: {e}", user_id=self.user_id)
            self._send_error_response(500, "Internal Server Error")

    def do_POST(self):
        try:
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
        except Exception as e:
            self.service.log_activity("EXCEPTION", f"Server Error: {e}", user_id=self.user_id)
            self._send_error_response(500, "Internal Server Error")

    def do_PUT(self):
        try:
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
        except Exception as e:
            self.service.log_activity("EXCEPTION", f"Server Error: {e}", user_id=self.user_id)
            self._send_error_response(500, "Internal Server Error")

    def do_DELETE(self):
        try:
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
        except Exception as e:
            self.service.log_activity("EXCEPTION", f"Server Error: {e}", user_id=self.user_id)
            self._send_error_response(500, "Internal Server Error")
