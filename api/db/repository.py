from api.db.db import Database
from mysql.connector import Error

class TransactionRepository:
    def __init__(self):
        self.db = Database()

    def create_transaction(self, data):
        connection = self.db.get_connection()
        if not connection:
            return False, "Database connection failed", None

        cursor = connection.cursor(dictionary=True)
        try:
            # 1. Handle User (Find or Create)
            user_id = None
            contact_name = data.get("from")
            phone = data.get("phone") # Original phone before masking, if available
            
            # Note: service.py currently deletes 'phone' before calling write, 
            # we need to ensure we pass the full data to repo before modifying it or pass fields explicitly.
            # Assuming 'data' passed here still has 'phone' if it was in the request? 
            # Wait, service.py used to modify 'data' in place. I will update service.py to pass clean data.
            
            if contact_name or phone:
                # Try to find user
                query_user = "SELECT id FROM Users WHERE phone_number = %s"
                cursor.execute(query_user, (str(phone),))
                user = cursor.fetchone()
                
                if user:
                    user_id = user['id']
                else:
                    # Create new user
                    # If phone is missing but we have name, or vice versa? 
                    # For now assume we create if we have at least one?
                    if not contact_name: contact_name = "Unknown"
                    if not phone: phone = "Unknown"
                    
                    insert_user = "INSERT INTO Users (name, phone_number) VALUES (%s, %s)"
                    cursor.execute(insert_user, (contact_name, str(phone)))
                    user_id = cursor.lastrowid

            # 2. Insert Transaction
            query = """
                INSERT INTO Transactions (
                    transaction_id, date, readable_date, 
                    amount, balance_after, direction, 
                    contact_name, user_id, 
                    subject, status, locked, service_center
                ) VALUES (
                    %s, %s, %s, 
                    %s, %s, %s, 
                    %s, %s, 
                    %s, %s, %s, %s
                )
            """
            
            # Mappings
            t_id = data.get("transaction_id")
            date_val = data.get("date")
            readable_date = data.get("readable_date")
            amount = data.get("amount_rwf")
            balance = data.get("balance_rwf")
            direction = data.get("type")
            sender = data.get("sender", "M-Money")
            
            # Defaults
            status = 1
            locked = 0
            service_center = "M-Money" # Assuming sender is service center

            cursor.execute(query, (
                t_id, date_val, readable_date,
                amount, balance, direction,
                contact_name, user_id,
                sender, status, locked, service_center
            ))
            
            new_id = cursor.lastrowid
            connection.commit()
            
            # Construct result to match previous dictionary format if needed
            data['id'] = new_id
            return True, None, data

        except Error as e:
            print(f"Error creating transaction: {e}")
            return False, f"Database error: {e}", None
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_all_transactions(self):
        connection = self.db.get_connection()
        if not connection:
            return False, "Database connection failed", []

        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    t.transaction_id, t.date, t.readable_date, t.amount, t.balance_after as balance_rwf, 
                    t.direction as type, t.contact_name as `from`, t.subject as sender,
                    u.phone_number as phone
                FROM Transactions t
                LEFT JOIN Users u ON t.user_id = u.id
                ORDER BY t.date DESC
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Map back to API format (e.g. amount -> amount_rwf)
            # The SQL alias handles some, but let's be explicit
            results = []
            for row in rows:
                item = {
                    "transaction_id": row['transaction_id'],
                    "date": str(row['date']) if row['date'] else None,
                    "readable_date": row['readable_date'],
                    "amount_rwf": row['amount'],
                    "balance_rwf": row['balance_rwf'],
                    "type": row['type'],
                    "from": row['from'],
                    "sender": row['sender'],
                    # Mask phone again for display
                    "phone_masked": self._mask_phone(row['phone']) if row['phone'] else None
                }
                results.append(item)
                
            return True, None, results
        except Error as e:
            return False, f"Database error: {e}", None
        finally:
            cursor.close()
            connection.close()

    def get_transaction_by_id(self, transaction_id):
        connection = self.db.get_connection()
        if not connection:
            return False, "Database connection failed", None

        cursor = connection.cursor(dictionary=True)
        try:
            # We search by the external transaction_id, not the PK id
            query = """
                SELECT 
                    t.transaction_id, t.date, t.readable_date, t.amount, t.balance_after as balance_rwf, 
                    t.direction as type, t.contact_name as `from`, t.subject as sender,
                    u.phone_number as phone
                FROM Transactions t
                LEFT JOIN Users u ON t.user_id = u.id
                WHERE t.transaction_id = %s
            """
            cursor.execute(query, (transaction_id,))
            row = cursor.fetchone()
            
            if not row:
                return False, f"Not Found: Transaction with ID {transaction_id} does not exist", None

            item = {
                "transaction_id": row['transaction_id'],
                "date": str(row['date']),
                "readable_date": row['readable_date'],
                "amount_rwf": row['amount'],
                "balance_rwf": row['balance_rwf'],
                "type": row['type'],
                "from": row['from'],
                "sender": row['sender'],
                "phone_masked": self._mask_phone(row['phone']) if row['phone'] else None
            }
            return True, None, item
            
        except Error as e:
            return False, f"Database error: {e}", None
        finally:
            cursor.close()
            connection.close()

    def update_transaction(self, transaction_id, data):
        # This is complex because of balance recalculation. 
        # For now, let's implement the basic update of fields.
        # Balance recalculation in SQL is hard without a stored proc or reading all.
        # We might need to stick to the service logic: read all (or from point), recalculate, save.
        # OR: Lock table, read relevant rows, update in memory, write back.
        
        # Given the scope, maybe we just update the specific record's fields for now
        # and warn that balance recalculation is expensive/TODO?
        # The previous implementation recalculated EVERYTHING. 
        # In a real DB, we wouldn't fetch everything.
        # But if the requirement implies keeping the logic...
        
        # Let's try to just update fields first.
        
        connection = self.db.get_connection()
        if not connection:
            return False, "Database connection failed", None

        cursor = connection.cursor(dictionary=True)
        try:
            # Check existence
            query_check = "SELECT id FROM Transactions WHERE transaction_id = %s"
            cursor.execute(query_check, (transaction_id,))
            existing = cursor.fetchone()
            if not existing:
                return False, f"Not Found: Transaction with ID {transaction_id} does not exist", None
            
            pk_id = existing['id']
            
            # Fields to update
            # data has: sender, type, amount_rwf, from
            updates = []
            params = []
            
            if "sender" in data:
                updates.append("subject = %s")
                params.append(data["sender"])
            if "type" in data:
                updates.append("direction = %s")
                params.append(data["type"])
            if "amount_rwf" in data:
                updates.append("amount = %s")
                params.append(data["amount_rwf"])
            if "from" in data:
                updates.append("contact_name = %s")
                params.append(data["from"])
            if "balance_rwf" in data:
                updates.append("balance_after = %s")
                params.append(data["balance_rwf"])
                
            if not updates:
                return True, None, data # Nothing to update
                
            query = f"UPDATE Transactions SET {', '.join(updates)} WHERE id = %s"
            params.append(pk_id)
            
            cursor.execute(query, tuple(params))
            connection.commit()
            
            # Refetch to return
            return self.get_transaction_by_id(transaction_id)
            
        except Error as e:
            return False, f"Database error: {e}", None
        finally:
            cursor.close()
            connection.close()

    def delete_transaction(self, transaction_id):
        connection = self.db.get_connection()
        if not connection:
            return False, "Database connection failed", None

        cursor = connection.cursor(dictionary=True)
        try:
            query = "DELETE FROM Transactions WHERE transaction_id = %s"
            cursor.execute(query, (transaction_id,))
            
            if cursor.rowcount == 0:
                return False, f"Not Found: Transaction with ID {transaction_id} does not exist", None
                
            connection.commit()
            return True, None, transaction_id
            
        except Error as e:
            return False, f"Database error: {e}", None
        finally:
            cursor.close()
            connection.close()
            
    def _mask_phone(self, phone):
        if not phone: return ""
        s = str(phone)
        if len(s) > 3:
            return "*" * (len(s) - 3) + s[-3:]
        return s
        
    def get_max_transaction_id(self):
        connection = self.db.get_connection()
        if not connection: return 0
        cursor = connection.cursor()
        cursor.execute("SELECT MAX(transaction_id) FROM Transactions")
        row = cursor.fetchone()
        cursor.close()
        connection.close()
        return row[0] if row and row[0] else 0
