import json
import os
from datetime import datetime

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

        required_fields = ["sender", "type", "amount_rwf", "from", "phone"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
             return False, f"Bad Request: Missing required fields ({', '.join(missing_fields)})", None
        
        # Validate type
        if data["type"] not in ["received", "sent"]:
            return False, "Bad Request: type must be 'received' or 'sent'", None
            
        # Validate amount
        if not isinstance(data["amount_rwf"], (int, float)) or data["amount_rwf"] <= 0:
            return False, "Bad Request: amount_rwf must be a positive number", None
            
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

    def get_all_transactions(self):
        """Retrieve all transactions from the data file."""
        transactions = self.read_transactions()
        return True, None, transactions

    def get_transaction_by_id(self, transaction_id):
        """Retrieve a single transaction by ID."""
        try:
            transaction_id = int(transaction_id)
        except (ValueError, TypeError):
            return False, "Bad Request: Invalid transaction ID format", None
        
        transactions = self.read_transactions()
        
        for transaction in transactions:
            if transaction.get("transaction_id") == transaction_id:
                return True, None, transaction
        
        return False, f"Not Found: Transaction with ID {transaction_id} does not exist", None

    def generate_transaction_id(self, transactions):
        max_id = 0
        for t in transactions:
            t_id = t.get("transaction_id", "")
            if isinstance(t_id, str) and t_id.isdigit():
                val = int(t_id)
                if val > max_id:
                    max_id = val
            elif isinstance(t_id, int):
                if t_id > max_id:
                    max_id = t_id
        return max_id + 1

    def write_transaction(self, data):
        transactions = self.read_transactions()
        
        # 1. Mask phone number
        raw_phone = str(data.get("phone", ""))
        if len(raw_phone) > 3:
            masked_phone = "*" * (len(raw_phone) - 3) + raw_phone[-3:]
        else:
            masked_phone = raw_phone
        data["phone_masked"] = masked_phone
        
        # 2. Generate transaction_id
        data["transaction_id"] = self.generate_transaction_id(transactions)
        
        # 3. Date and readable_date
        now = datetime.now()
        data["date"] = now.strftime("%Y-%m-%dT%H:%M:%S")
        # example: "10 May 2024 4:30:58 PM"
        data["readable_date"] = now.strftime("%d %b %Y %I:%M:%S %p")
        
        # 4. Calculate balance
        current_balance = 0
        if transactions:
            # Assuming the list is ordered by time
            last_item = transactions[-1]
            current_balance = last_item.get("balance_rwf", 0)
            
        amount = data["amount_rwf"]
        transaction_type = data["type"]
        
        if transaction_type == "received":
            new_balance = current_balance + amount
        elif transaction_type == "sent":
            if current_balance < amount:
                return False, f"Bad Request: Insufficient funds. Available balance: {current_balance}"
            new_balance = current_balance - amount
        else:
            return False, "Bad Request: Invalid transaction type"
            
        data["balance_rwf"] = new_balance
        
        # Remove original 'phone' field because we will only store the phone_masked
        if "phone" in data:
            del data["phone"]

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
