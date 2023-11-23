import sqlite3
import mysql.connector
import json

def transfer_table_data(sqlite_cursor, mysql_cursor, table_name, unique_field):
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    rows = sqlite_cursor.fetchall()
    for row in rows:
        # Construct a query to check for duplicates
        # Assuming the unique field is the first field in each row
        check_query = f"SELECT * FROM {table_name} WHERE {unique_field} = %s"
        mysql_cursor.execute(check_query, (row[0],))

        if mysql_cursor.fetchone() is None:
            # Construct a query to insert data
            placeholders = ', '.join(['%s'] * len(row))
            insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
            mysql_cursor.execute(insert_query, row)

def transfer_data():
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

    # Define your tables and their unique fields
    tables = {
        'VM': 'VM_ID',
        'Inventory': 'Item_ID',  # Assuming Item_ID is unique in Inventory
        'Transaction_History': 'Transaction_ID',  # Assuming Transaction_ID is unique
        'Items': 'Item_ID'
    }

    # Transfer data for each table
    for table_name, unique_field in tables.items():
        transfer_table_data(sqlite_cursor, mysql_cursor, table_name, unique_field)

    # Commit and close connections
    mysql_conn.commit()
    mysql_conn.close()
    sqlite_conn.close()

# # Call the function to start transfer
# transfer_data()
