import json
from datetime import datetime
from pydantic import ValidationError

from api.auth import is_authenticated as check_auth
from api.db.repository import TransactionRepository, LogRepository
from api.db.models import TransactionCreate, TransactionUpdate, LogCreate


class SMSTransactionsService:
    def __init__(self):
        self.repository = TransactionRepository()
        self.log_repository = LogRepository()

    def is_authenticated(self, headers):
        return check_auth(headers)

    def log_activity(self, log_type, message, transaction_id=None, user_id=None):
        try:
            log_data = {
                "type": log_type,
                "message": message,
                "transaction_id": transaction_id,
                "user_id": user_id
            }
            # Validate using model before sending to repo (optional but good practice)
            # log_model = LogCreate(**log_data) 
            # We skip strict model check here to avoid breaking logging on error, but repo handles it.
            self.log_repository.create_log(log_data)
        except Exception as e:
            print(f"Failed to write log: {e}")

    def get_all_logs(self):
        return self.log_repository.get_all_logs()

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
            json_data = json.loads(post_data.decode('utf-8'))
            
            # Validate with Pydantic
            transaction_data = TransactionCreate(**json_data)
            return True, None, transaction_data.model_dump()
            
        except json.JSONDecodeError:
            return False, "Bad Request: Invalid JSON", None
        except ValidationError as e:
             # Format Pydantic errors nicely
            errors = []
            for err in e.errors():
                field = ".".join(str(x) for x in err['loc'])
                msg = err['msg']
                errors.append(f"{field}: {msg}")
            return False, f"Validation Error: {'; '.join(errors)}", None
        except Exception as e:
            return False, f"Bad Request: {str(e)}", None

    def validate_update_transaction_request(self, headers, rfile):
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
            json_data = json.loads(post_data.decode('utf-8'))
            
            # Validate with Pydantic
            transaction_data = TransactionUpdate(**json_data)
            return True, None, transaction_data.model_dump(exclude_unset=True)
            
        except json.JSONDecodeError:
            return False, "Bad Request: Invalid JSON", None
        except ValidationError as e:
            errors = []
            for err in e.errors():
                field = ".".join(str(x) for x in err['loc'])
                msg = err['msg']
                errors.append(f"{field}: {msg}")
            return False, f"Validation Error: {'; '.join(errors)}", None
        except Exception:
            return False, "Bad Request: Could not read content", None

    def get_all_transactions(self):
        success, error, data = self.repository.get_all_transactions()
        if success:
            self.log_activity("INFO", "Fetched all transactions")
        else:
            self.log_activity("ERROR", f"Failed to fetch transactions: {error}")
        return success, error, data

    def get_transaction_by_id(self, transaction_id):
        try:
            transaction_id = int(transaction_id)
        except (ValueError, TypeError):
            return False, "Bad Request: Invalid transaction ID format", None
        
        success, error, data = self.repository.get_transaction_by_id(transaction_id)
        if success:
            self.log_activity("INFO", f"Fetched transaction {transaction_id}", transaction_id=transaction_id)
        else:
            self.log_activity("ERROR", f"Failed to fetch transaction {transaction_id}: {error}")
        return success, error, data

    def generate_transaction_id(self):
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
        success, error, transactions = self.repository.get_all_transactions()
        current_balance = 0
        if success and transactions:
            # Assuming first item is latest based on sort order
            current_balance = transactions[0].get("balance_rwf", 0)

        # Ensure we have defaults because Pydantic models might exclude them if not set, 
        # but here we rely on what passed validation.
        amount = data["amount"]
        transaction_type = data["direction"]

        if transaction_type == "received":
            new_balance = current_balance + amount
        elif transaction_type == "sent":
            if current_balance < amount:
                self.log_activity("WARNING", f"Insufficient funds for transaction attempt. Amount: {amount}, Balance: {current_balance}")
                return False, f"Bad Request: Insufficient funds. Available balance: {current_balance}", None
            new_balance = current_balance - amount
        else:
            return False, "Bad Request: Invalid transaction direction", None
        
        data["balance_rwf"] = new_balance
        
        # Map fields for Repository
        # Repository expects keys: amount_rwf, type, from, sender
        # Data from Pydantic has: amount, direction, contact_name, sender
        
        repo_data = data.copy()
        repo_data["amount_rwf"] = data["amount"]
        repo_data["type"] = data["direction"]
        repo_data["from"] = data["contact_name"]
        
        # Pass to Repository
        success, error, created_data = self.repository.create_transaction(repo_data)
        
        if success:
            # Re-map for response? Or return what repo returned?
            # Repo returns with ID and formatted fields? 
            # Repo returns 'data' which is the input dict + 'id'.
            # We might want to construct a clean response.
            t_id = created_data.get("transaction_id")
            self.log_activity("INFO", f"Created transaction {t_id}", transaction_id=t_id)
        else:
            self.log_activity("ERROR", f"Failed to create transaction: {error}")
            
        return success, error, created_data

    def update_transaction(self, transaction_id, data):
        try:
            t_id = int(transaction_id)
        except ValueError:
            return False, "Bad Request: Invalid ID", None
            
        # Map fields for Repo
        repo_data = data.copy()
        if "amount" in data: repo_data["amount_rwf"] = data["amount"]
        if "direction" in data: repo_data["type"] = data["direction"]
        if "contact_name" in data: repo_data["from"] = data["contact_name"]
            
        success, error, updated_transaction = self.repository.update_transaction(t_id, repo_data)
        
        if success:
             self.log_activity("INFO", f"Updated transaction {transaction_id}", transaction_id=t_id)
        else:
             self.log_activity("ERROR", f"Failed to update transaction {transaction_id}: {error}")
             
        return success, error, updated_transaction

    def delete_transaction(self, transaction_id):
        try:
            t_id = int(transaction_id)
        except ValueError:
            return False, "Bad Request: Invalid ID", None
            
        success, error, deleted_id = self.repository.delete_transaction(t_id)
        
        if success:
            self.log_activity("INFO", f"Deleted transaction {transaction_id}", transaction_id=t_id)
        else:
            self.log_activity("ERROR", f"Failed to delete transaction {transaction_id}: {error}")
            
        return success, error, deleted_id

    def response(self, handler, status_code, data):
        handler.send_response(status_code)
        handler.send_header('Content-type', 'application/json')
        if status_code == 401:
            handler.send_header('WWW-Authenticate', 'Basic realm="Momo API"')
        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode())
