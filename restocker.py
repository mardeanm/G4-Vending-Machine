# restocker.py
import sqlite3
from flask import jsonify, request


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
