#if not in use standby
#show product options w/ price, quantity available
# adding the items to cart
#check out
#be able to cancel the order
#cash or card transaction an their implications
#if card deny wait for different payment
#update the database
#offer recipet through phone or none
#go back to standby
#if afk go to stand by mode clearing the cart
#Just create a website in Python using Flask or Django or some other python web
# framework and then turn it into a Desktop app with Electron. Discord for example uses this method.
#--use
# SELECT COUNT(*)
#FROM Products;
# to update batch
from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timedelta
app = Flask(__name__)

VM_ID=1
def get_items():
    conn = sqlite3.connect('vending_machines_DB.sqlite.db')
    cur = conn.cursor()

    # Fetch item details
    cur.execute("SELECT Item_ID, Price FROM Items")
    items = {item[0]: item[1] for item in cur.fetchall()}

    # Fetch quantities for each item
    cur.execute("SELECT Item_ID, SUM(Quantity) as TotalQuantity FROM Inventory GROUP BY Item_ID")
    quantities = {row[0]: row[1] for row in cur.fetchall()}

    conn.close()
    return items,quantities
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
class Cart:
    def __init__(self):
        self.items = {}  # Format: {item_id: {'quantity': quantity, 'name': name, 'price': price}}

    def add_item(self, item_id, quantity, name, price):
        if item_id in self.items:
            self.items[item_id]['quantity'] += quantity
        else:
            self.items[item_id] = {'quantity': quantity, 'name': name, 'price': price}

    def check_out(self):
        # Checkout logic here
        pass

cart = Cart()

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    item_id = data['item_id']
    quantity = data['quantity']
    # Fetch item details like name and price from the database
    # For example:
    name = "Item Name"  # Replace with actual database query
    price = 10.00       # Replace with actual database query

    cart.add_item(item_id, quantity, name, price)
    return jsonify(success=True)

# @app.route('/')
# def update_expiration_route():
#     update_expiration_dates('vending_machines_DB.sqlite.db')
#     return "Expiration dates updated successfully!"
@app.route('/')
def index():
   items,quantities=get_items()
   return render_template('index.html', items=items, quantities=quantities)

if __name__ == '__main__':

    app.run()
# from apscheduler.schedulers.background import BackgroundScheduler
#
# # ... (rest of your imports and update_expiration_dates function)
#
# def start_scheduler():
#     scheduler = BackgroundScheduler()
#     scheduler.add_job(func=update_expiration_dates, trigger="interval", days=1)
#     scheduler.start()
#
# # ... (rest of your app.py)
#
# if __name__ == '__main__':
#     start_scheduler()
#     app.run()


#Ignore for now
 # conn = sqlite3.connect('vending_machines_DB.sqlite.db')
    # cur = conn.cursor()
    #
    # # Fetch item details
    # cur.execute("SELECT Item_ID, Price FROM Items")
    # items = {item[0]: item[1] for item in cur.fetchall()}
    #
    # # Fetch quantities for each item
    # cur.execute("SELECT Item_ID, SUM(Quantity) as TotalQuantity FROM Inventory GROUP BY Item_ID")
    # quantities = {row[0]: row[1] for row in cur.fetchall()}
    #
    # conn.close()
