# restocker.py
import sqlite3
from flask import jsonify, request

VM_ID=1

def update_expiration_dates(db_path):

# Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # SQL to update the expiration date in the inventory table
    # This assumes 'Purchase_date' is stored in a format that SQLite can perform date calculations on
    # and 'shelf_life' is stored as an integer number of weeks in the items table.
    update_sql = """
    UPDATE Inventory  -- Make sure this matches the table name's case in the database
    SET Expiration_Date = (
        SELECT date(Stock_Date, '+' || (Items.Shelf_Life * 7) || ' days')
        FROM Items
        WHERE Items.Item_ID = Inventory.Item_ID
    )
    WHERE Inventory.Item_ID IN (SELECT Item_ID FROM Items)
    """

    # Execute the SQL command
    cur.execute(update_sql)

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()
def update_inventory(item_id, quantity):
    conn = sqlite3.connect('vending_machines_DB.sqlite.db')
    cur = conn.cursor()

    # Check if the item exists in the inventory
    cur.execute("SELECT Quantity FROM Inventory WHERE Item_ID = ?", (item_id,))
    result = cur.fetchone()

    if result:
        # Update the quantity if the item exists
        new_quantity = result[0] + quantity
        cur.execute(
            "UPDATE Inventory SET Quantity = ? WHERE Item_ID = ?", (new_quantity, item_id))
    else:
        # Insert new item into inventory if it doesn't exist
        cur.execute(
            "INSERT INTO Inventory (Item_ID, Quantity) VALUES (?, ?)", (item_id, quantity))

    conn.commit()
    conn.close()


def restock():
    data = request.json
    item_id = data['item_id']
    quantity = data['quantity']

    try:
        update_inventory(item_id, quantity)
        return jsonify(success=True, message="Restocking completed"), 200
    except sqlite3.Error as e:
        return jsonify(success=False, message=str(e)), 500
