import json
from http.server import BaseHTTPRequestHandler
from api.service import SMSTransactionsService

class SMSTransactionsController(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.service = SMSTransactionsService()
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path != '/transactions':
            self.send_error(404, "Not Found")
            return

        if not self.service.is_authenticated(self.headers):
            self.service.response(self, 401, {"error": "Unauthorized: Invalid or missing credentials"})
            return

        transactions = self.service.read_transactions()
        self.service.response(self, 200, transactions)

    def do_POST(self):
        if self.path != '/transactions':
            self.send_error(404, "Not Found")
            return

        if not self.service.is_authenticated(self.headers):
            self.service.response(self, 401, {"error": "Unauthorized: Invalid or missing credentials"})
            return

        is_valid, error, data = self.service.validate_create_transaction_request(self.headers, self.rfile)
        if not is_valid:
             self.service.response(self, 400, {"error": error})
             return

        success, error = self.service.write_transaction(data)
        if not success:
             self.service.response(self, 500, {"error": error})
             return

        self.service.response(self, 201, {
            "status": "success",
            "message": "Transaction created successfully",
            "data": data
        })
