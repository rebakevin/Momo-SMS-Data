from http.server import BaseHTTPRequestHandler
import re

from api.routes import ROUTES
from api.service import SMSTransactionsService


class SMSTransactionsController(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.service = SMSTransactionsService()
        super().__init__(*args, **kwargs)

    def handle_route(self, method):
        routes = ROUTES.get(method, {})

        # 1️⃣ Try exact (static) routes first
        if self.path in routes:
            routes[self.path](self)
            return

        # 2️⃣ Try dynamic routes like /transactions/{id}
        for route, handler in routes.items():
            if "{id}" in route:
                # Convert /transactions/{id} → /transactions/(\d+)
                pattern = route.replace("{id}", r"(\d+)")
                match = re.fullmatch(pattern, self.path)

                if match:
                    # Store extracted path parameters
                    self.path_params = {
                        "id": match.group(1)
                    }
                    handler(self)
                    return

        # 3️⃣ No route matched
        self.send_error(404, "Not Found")

    def do_GET(self):
        self.handle_route("GET")

    def do_POST(self):
        self.handle_route("POST")
