import json
import os
from api.auth import is_authenticated as check_auth

class SMSTransactionsService:
    DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'sample.json')

    def is_authenticated(self, headers):
        return check_auth(headers)

    def validate_create_transaction_request(self, headers, rfile):
        content_length_header = headers.get('Content-Length')
        if not content_length_header:
             return False, "Bad Request: No content provided", None
             
        try:
            content_length = int(content_length_header)
        except ValueError:
            return False, "Bad Request: Invalid Content-Length", None

        if content_length == 0:
            return False, "Bad Request: No content provided", None

        try:
            post_data = rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            return False, "Bad Request: Invalid JSON", None
        except Exception:
            return False, "Bad Request: Could not read content", None

        required_fields = ["sender", "amount_rwf", "transaction_id"]
        if not all(field in data for field in required_fields):
             return False, "Bad Request: Missing required fields (sender, amount_rwf, transaction_id)", None
        return True, None, data

    def read_transactions(self):
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r') as f:
                    content = f.read()
                    if content:
                        return json.loads(content)
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def write_transaction(self, data):
        transactions = self.read_transactions()
        transactions.append(data)
        
        try:
            with open(self.DATA_FILE, 'w') as f:
                json.dump(transactions, f, indent=4)
            return True, None
        except IOError:
            return False, "Internal Server Error: Could not save transaction"

    def response(self, handler, status_code, data):
        handler.send_response(status_code)
        handler.send_header('Content-type', 'application/json')
        
        if status_code == 401:
            handler.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
            
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode())
