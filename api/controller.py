from http.server import BaseHTTPRequestHandler

from api.routes import ROUTES
from api.service import SMSTransactionsService


class SMSTransactionsController(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.service = SMSTransactionsService()
        super().__init__(*args, **kwargs)

    def handle_route(self, method):
        handler = ROUTES.get(method, {}).get(self.path)

        if not handler:
            self.send_error(404, "Not Found")
            return

        handler(self)

    def do_GET(self):
        self.handle_route("GET")

    def do_POST(self):
        self.handle_route("POST")
