import mysql.connector
import os
from api.db.db import Database

def run_migration():
    print("Starting migration...")
    db = Database()
    
    # Read SQL file
    sql_file = os.path.join(os.path.dirname(__file__), 'database', 'database_setup.sql')
    if not os.path.exists(sql_file):
        print(f"Error: {sql_file} not found.")
        return

    with open(sql_file, 'r') as f:
        sql_commands = f.read()



    commands = sql_commands.split(';')
    
    connection = db.get_connection()
    if not connection:
        print("Failed to connect to database. Ensure Docker container is running.")
        return

    cursor = connection.cursor()
    try:
        for command in commands:
            command = command.strip()
            if command:
                print(f"Executing: {command[:50]}...")
                cursor.execute(command)
        connection.commit()
        print("Migration completed successfully.")
    except mysql.connector.Error as e:
        print(f"Error executing migration: {e}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    run_migration()
