from flask import Flask, render_template, request, jsonify
import sqlite3
import mysql.connector
import json
from datetime import datetime, timedelta



def get_expired_items():
    with sqlite3.connect('vending_machines_DB.sqlite.db') as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT Inventory.Item_ID, Items.Item_Name, Inventory.Quantity, Inventory.Expiration_Date 
            FROM Inventory 
            INNER JOIN Items ON Inventory.Item_ID = Items.Item_ID
            WHERE Inventory.Expiration_Date <= ?
        """, (datetime.now() + timedelta(weeks=1),))
        expired_items = cur.fetchall()
    return expired_items

def get_low_stock_items(quantities,items,low_stock_threshold=5):

    low_stock_items = []
    for item_id, quantity in quantities.items():
        if quantity <= low_stock_threshold:
            item_info = items.get(item_id, {})

            low_stock_items.append({
                'Item_ID': item_id,
                'Item_Name': item_info.get('name', 'Unknown'),
                'Quantity': quantity
            })

    return low_stock_items

def get_instructions(VM_ID):
    # Connect to MySQL and fetch instructions
    # Return either the instructions or "No Instructions"
    try:
        with open('config.json') as config_file:
            config = json.load(config_file)

        mysql_conn = mysql.connector.connect(
            host=config["host"],
            user=config["mysql_user"],
            password=config["mysql_password"],
            database=config["database"]
        )
        mysql_conn = mysql_conn
        mysql_cursor = mysql_conn.cursor()

        # Assuming 'VM_ID' is the column to match and it's stored in a variable VM_ID
        mysql_cursor.execute("SELECT Instructions FROM VM WHERE VM_ID = %s", (VM_ID,))
        result = mysql_cursor.fetchone()

        # Check if result is not None and Instructions is not null
        instructions = result[0] if result and result[0] is not None else "No Instructions"

        return instructions

    except mysql.connector.Error as err:
        print("Error occurred:", err)
        return "No Instructions"
    finally:
        mysql_cursor.close()
        mysql_conn.close()



def add_to_inventory(VM_ID):
    data = request.json
    item_id = data.get('item_id')
    quantity = data.get('quantity')

    try:
        conn = sqlite3.connect('vending_machines_DB.sqlite.db')
        cur = conn.cursor()

        # Get shelf life of the item
        cur.execute("SELECT Shelf_Life FROM Items WHERE Item_ID = ?", (item_id,))
        shelf_life = cur.fetchone()
        if not shelf_life:
            return jsonify({'success': False, 'message': 'Item not found'}), 404

        # Calculate expiration date
        expiration_date = datetime.now() + timedelta(weeks=shelf_life[0])

        # Set stock date to current date
        stock_date = datetime.now().strftime("%Y-%m-%d")

        # Insert into Inventory
        cur.execute("INSERT INTO Inventory (VM_ID, Item_ID, Quantity, Expiration_Date, Stock_Date) VALUES (?, ?, ?, ?, ?)",
                    (VM_ID, item_id, quantity, expiration_date.strftime("%Y-%m-%d"), stock_date))

        conn.commit()
        return jsonify({'success': True, 'message': 'Item added successfully'}), 200

    except sqlite3.Error as e:
        return jsonify({'success': False, 'message': str(e)}), 500

    finally:
        conn.close()
