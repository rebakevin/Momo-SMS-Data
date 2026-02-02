from api.db import Database
from api.models import Transaction, User
import mysql.connector

class TransactionRepository:
    def __init__(self):
        self.db = Database()

    def create(self, data: dict):
        connection = self.db.get_connection()
        if not connection:
            return False, "Database connection failed"

        cursor = connection.cursor(dictionary=True)
        try:
            # Check/Create User if phone is provided (Assuming phone maps to User)
            # This is a simplification. Ideally, we should look up user by phone or create one.
            # For this migration, we'll skip complex user logic and focus on Transaction.
            
            # Map fields
            query = """
                INSERT INTO Transactions (
                    transaction_id, date, amount, readable_date, 
                    direction, status, balance_after, contact_name, 
                    phone_masked, sender
                ) VALUES (
                     %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """
            # Note: The SQL schema has specific columns. 
            # JSON keys: sender, amount_rwf, type (received/sent), from, phone_masked, transaction_id, date, readable_date, balance_rwf
            # SQL columns: id, date, subject, body, status, service_center, read, locked, date_sent, readable_date, contact_name, transaction_id, amount, balance_after, direction, category_id, user_id
            
            # Additional Mapping needed: 
            # amount_rwf -> amount
            # type -> direction
            # from -> contact_name? 
            # balance_rwf -> balance_after
            
            # Wait, the SQL schema doesn't have 'sender' or 'phone_masked' columns based on my previous view.
            # I must check the SQL schema I applied.
            
            pass 
        except mysql.connector.Error as e:
            return False, f"Database error: {e}"
        finally:
            cursor.close()
            connection.close()

    def get_all(self):
        pass
