from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from api.auth import is_authenticated

class SMSTransactionsHandler(BaseHTTPRequestHandler):
    
    def _send_error_response(self, status_code, message):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')

        if status_code == 401:
            self.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
        
        self.end_headers()
        response = {"error": message}

        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        # This acts like an authentication middleware
        if not is_authenticated(self.headers):
            self._send_error_response(
                401, "Unauthorized: Invalid or missing credentials")
            return

        # Continue with your logic here...