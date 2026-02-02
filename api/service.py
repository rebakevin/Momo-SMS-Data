import json
from datetime import datetime

from api.auth import is_authenticated as check_auth
from api.db.repository import TransactionRepository


class SMSTransactionsService:
    def __init__(self):
        self.repository = TransactionRepository()

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

        # Updated required fields to match SQL models/New API contract
        # OLD: sender, type, amount_rwf, from, phone
        # NEW: sender, direction, amount, contact_name, phone
        required_fields = ["sender", "direction", "amount", "contact_name", "phone"]
        missing_fields = [
            field for field in required_fields if field not in data]

        if missing_fields:
            return False, f"Bad Request: Missing required fields ({', '.join(missing_fields)})", None

        # Validate direction
        if data["direction"] not in ["received", "sent"]:
            return False, "Bad Request: direction must be 'received' or 'sent'", None

        # Validate amount
        if not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
            return False, "Bad Request: amount must be a positive number", None

        return True, None, data

    def validate_update_transaction_request(self, headers, rfile):
        """Validate partial update request - only provided fields are required"""
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

        # Only validate fields that are provided
        if "direction" in data and data["direction"] not in ["received", "sent"]:
            return False, "Bad Request: direction must be 'received' or 'sent'", None

        if "amount" in data:
            if not isinstance(data["amount"], (int, float)) or data["amount"] <= 0:
                return False, "Bad Request: amount must be a positive number", None

        return True, None, data

    def get_all_transactions(self):
        return self.repository.get_all_transactions()

    def get_transaction_by_id(self, transaction_id):
        try:
            transaction_id = int(transaction_id)
        except (ValueError, TypeError):
            return False, "Bad Request: Invalid transaction ID format", None
        
        return self.repository.get_transaction_by_id(transaction_id)

    def generate_transaction_id(self):
        # We need the MAX ID. Repo helper or get_all.
        max_id = self.repository.get_max_transaction_id()
        return max_id + 1

    def write_transaction(self, data):
        # 1. Generate transaction_id
        data["transaction_id"] = self.generate_transaction_id()

        # 2. Date and readable_date
        now = datetime.now()
        data["date"] = now.strftime("%Y-%m-%dT%H:%M:%S")
        data["readable_date"] = now.strftime("%d %b %Y %I:%M:%S %p")

        # 3. Calculate balance
        # Fetch latest transaction to get current balance
        # Note: repo.get_all returns DESC by date, so first item is latest
        success, error, transactions = self.repository.get_all_transactions()
        current_balance = 0
        if success and transactions:
            current_balance = transactions[0].get("balance_rwf", 0)

        amount = data["amount"]
        transaction_type = data["direction"]

        if transaction_type == "received":
            new_balance = current_balance + amount
        elif transaction_type == "sent":
            if current_balance < amount:
                return False, f"Bad Request: Insufficient funds. Available balance: {current_balance}"
            new_balance = current_balance - amount
        else:
            return False, "Bad Request: Invalid transaction direction"

        # Map to usage inside App (JSON fields vs Internal)
        # Service uses internal keys 'balance_rwf' but repo expects what?
        # Repo create expects: amount_rwf (mapped to amount), balance_rwf, type (direction), from, phone ...
        # My Repo implementation maps:
        # amount_rwf -> amount
        # balance_rwf -> balance_after
        # type -> direction
        # from -> contact_name
        
        # BUT I changed validation to expect 'amount', 'direction'.
        # So I should align data keys before sending to repo.
        
        data["balance_rwf"] = new_balance
        # data["amount_rwf"] = amount # Repo expects 'amount_rwf' or did I write repo to expect 'amount'?
        # Checking repo draft:
        # amount = data.get("amount_rwf")  <-- Repo expects amount_rwf
        # direction = data.get("type")     <-- Repo expects type
        # So I need to map NEW keys back to OLD keys for Repo if I didn't update Repo?
        # OR Update Repo to match NEW keys.
        
        # Let's update data to match what Repo currently expects (based on my previous tool call for repository.py)
        # Repo.create_transaction uses:
        # data.get("amount_rwf")
        # data.get("balance_rwf")
        # data.get("type")
        
        data["amount_rwf"] = data["amount"]
        data["type"] = data["direction"]
        data["balance_rwf"] = new_balance
        
        # Pass to Repository
        return self.repository.create_transaction(data)

    def update_transaction(self, transaction_id, data):
        # This is strictly more complex with DB.
        # For this task, I will delegate to Repo update.
        # Note: Balance update logic is temporarily simplified/disabled in Repo for update.
        try:
            t_id = int(transaction_id)
        except ValueError:
            return False, "Bad Request: Invalid ID", None
            
        # Map fields for Repo
        if "amount" in data: data["amount_rwf"] = data["amount"]
        if "direction" in data: data["type"] = data["direction"]
        if "contact_name" in data: data["from"] = data["contact_name"]
            
        return self.repository.update_transaction(t_id, data)

    def delete_transaction(self, transaction_id):
        try:
            t_id = int(transaction_id)
        except ValueError:
            return False, "Bad Request: Invalid ID", None
            
        return self.repository.delete_transaction(t_id)

    def response(self, handler, status_code, data):
        handler.send_response(status_code)
        handler.send_header('Content-type', 'application/json')
        if status_code == 401:
            handler.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode())
