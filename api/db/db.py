import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.config = {
                'host': 'localhost',
                'database': 'momo_sms_app',
                'user': 'admin',
                'password': 'root', 
                'port': 3307
            }
            if os.getenv('DB_HOST'): cls._instance.config['host'] = os.getenv('DB_HOST')
            if os.getenv('DB_NAME'): cls._instance.config['database'] = os.getenv('DB_NAME')
            if os.getenv('DB_USER'): cls._instance.config['user'] = os.getenv('DB_USER')
            if os.getenv('DB_PASSWORD'): cls._instance.config['password'] = os.getenv('DB_PASSWORD')
            if os.getenv('DB_PORT'): cls._instance.config['port'] = int(os.getenv('DB_PORT'))

        return cls._instance

    def get_connection(self):
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return None
