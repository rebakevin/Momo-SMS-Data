import json
import os
from datetime import datetime

from api.auth import is_authenticated as check_auth


class SMSTransactionsService:
    DATA_FILE = os.path.join(os.path.dirname(
        os.path.dirname(__file__)), 'assets', 'transactions.json')

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
        missing_fields = [
            field for field in required_fields if field not in data]

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
        transactions = self.read_transactions()
        return True, None, transactions

    def get_transaction_by_id(self, transaction_id):
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

    def update_transaction(self, transaction_id, data):
        """Update an existing transaction with new data"""
        try:
            target_id = int(transaction_id)
        except (ValueError, TypeError):
            return False, "Bad Request: Invalid transaction ID format", None

        transactions = self.read_transactions()

        # Find the transaction to update
        transaction_index = None
        for idx, t in enumerate(transactions):
            if t.get("transaction_id") == target_id:
                transaction_index = idx
                break

        if transaction_index is None:
            return False, f"Not Found: Transaction with ID {target_id} does not exist", None

        # Validate updatable fields
        updatable_fields = ["sender", "type", "amount_rwf", "from", "phone"]
        update_data = {}

        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]

        # Validate type if provided
        if "type" in update_data and update_data["type"] not in ["received", "sent"]:
            return False, "Bad Request: type must be 'received' or 'sent'", None

        # Validate amount if provided
        if "amount_rwf" in update_data:
            if not isinstance(update_data["amount_rwf"], (int, float)) or update_data["amount_rwf"] <= 0:
                return False, "Bad Request: amount_rwf must be a positive number", None

        # Get the current transaction
        current_transaction = transactions[transaction_index]

        # Update phone mask if phone is updated
        if "phone" in update_data:
            raw_phone = str(update_data["phone"])
            if len(raw_phone) > 3:
                masked_phone = "*" * (len(raw_phone) - 3) + raw_phone[-3:]
            else:
                masked_phone = raw_phone
            current_transaction["phone_masked"] = masked_phone
            del update_data["phone"]

        # Update simple fields
        for field in ["sender", "type", "from", "amount_rwf"]:
            if field in update_data:
                current_transaction[field] = update_data[field]

        # If amount or type changed, recalculate balance
        if "amount_rwf" in update_data or "type" in update_data:
            # Recalculate balance from the beginning
            new_balance = 0
            for idx, transaction in enumerate(transactions):
                if idx < transaction_index:
                    # Keep existing balances before the updated transaction
                    new_balance = transaction.get("balance_rwf", 0)
                elif idx == transaction_index:
                    # Calculate new balance for updated transaction
                    amount = current_transaction.get("amount_rwf", 0)
                    trans_type = current_transaction.get("type", "received")

                    if trans_type == "received":
                        new_balance = new_balance + amount
                    elif trans_type == "sent":
                        if new_balance < amount:
                            return False, f"Bad Request: Insufficient funds for this transaction. Available balance: {new_balance}", None
                        new_balance = new_balance - amount

                    current_transaction["balance_rwf"] = new_balance
                else:
                    # Recalculate all balances after the updated transaction
                    amount = transaction.get("amount_rwf", 0)
                    trans_type = transaction.get("type", "received")

                    if trans_type == "received":
                        new_balance = new_balance + amount
                    elif trans_type == "sent":
                        new_balance = new_balance - amount

                    transaction["balance_rwf"] = new_balance

        # Update the transaction in the list
        transactions[transaction_index] = current_transaction

        try:
            with open(self.DATA_FILE, 'w') as f:
                json.dump(transactions, f, indent=4)
            return True, None, current_transaction
        except IOError:
            return False, "Internal Server Error: Could not update transaction", None

    def delete_transaction(self, transaction_id):
        transactions = self.read_transactions()

        try:
            target_id = int(transaction_id)
        except (ValueError, TypeError):
            return False, "Bad Request: Invalid transaction ID format", None

        original_count = len(transactions)
        transactions = [t for t in transactions if int(
            t.get("transaction_id", -1)) != target_id]

        if len(transactions) == original_count:
            return False, f"Not Found: Transaction with ID {target_id} not found", None

        try:
            with open(self.DATA_FILE, 'w') as f:
                json.dump(transactions, f, indent=4)
            return True, None, target_id
        except IOError:
            return False, "Internal Server Error: Could not delete transaction", None

    def response(self, handler, status_code, data):
        handler.send_response(status_code)
        handler.send_header('Content-type', 'application/json')

        if status_code == 401:
            handler.send_header('WWW-Authenticate', 'Basic realm="Momo API"')

        handler.end_headers()
        handler.wfile.write(json.dumps(data).encode())
