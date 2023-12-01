import sqlite3
import mysql.connector
import json

def transfer_inventory_data(sqlite_cursor, mysql_cursor, vm_id):
    # Check and delete existing records for the given VM_ID in MySQL
    mysql_cursor.execute("SELECT * FROM Inventory WHERE VM_ID = %s", (vm_id,))
    mysql_records = mysql_cursor.fetchall()

    sqlite_cursor.execute("SELECT * FROM Inventory WHERE VM_ID = ?", (vm_id,))
    sqlite_records = sqlite_cursor.fetchall()

    if set(mysql_records) != set(sqlite_records):
        mysql_cursor.execute("DELETE FROM Inventory WHERE VM_ID = %s", (vm_id,))

        # Insert all records from SQLite
        for row in sqlite_records:
            placeholders = ', '.join(['%s'] * len(row))
            insert_query = f"INSERT INTO Inventory VALUES ({placeholders})"
            mysql_cursor.execute(insert_query, row)

def transfer_transaction_history(sqlite_cursor, mysql_cursor, vm_id):
    # Find the latest transaction ID for the given VM_ID in MySQL
    mysql_cursor.execute("SELECT MAX(Transaction_ID) FROM Transaction_History WHERE VM_ID = %s", (vm_id,))
    max_transaction_id = mysql_cursor.fetchone()[0] or 0

    # Transfer new transactions from SQLite
    sqlite_cursor.execute("SELECT * FROM Transaction_History WHERE VM_ID = ? AND Transaction_ID > ?", (vm_id, max_transaction_id))
    new_transactions = sqlite_cursor.fetchall()

    for transaction in new_transactions:
        placeholders = ', '.join(['%s'] * len(transaction))
        insert_query = f"INSERT INTO Transaction_History VALUES ({placeholders})"
        mysql_cursor.execute(insert_query, transaction)

def transfer_data(vm_id):
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('vending_machines_DB.sqlite.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to MySQL
    with open('config.json') as config_file:
        config = json.load(config_file)

    mysql_conn = mysql.connector.connect(
        host=config["host"],
        user=config["mysql_user"],
        password=config["mysql_password"],
        database=config["database"]
    )
    mysql_cursor = mysql_conn.cursor()

    # Transfer data for Inventory and Transaction_History
    transfer_inventory_data(sqlite_cursor, mysql_cursor, vm_id)
    transfer_transaction_history(sqlite_cursor, mysql_cursor, vm_id)

    # Commit and close connections
    mysql_conn.commit()
    mysql_conn.close()
    sqlite_conn.close()
