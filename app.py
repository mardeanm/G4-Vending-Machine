
from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
import json
import mysql
from apscheduler.schedulers.background import BackgroundScheduler
import DB_updater
import datetime

app = Flask(__name__)
VM_ID=1
Max_Quantity=8
items={}
quantities={}
item_ids=[]


def get_items():
    global items, quantities  # Use global variables
    conn = sqlite3.connect('vending_machines_DB.sqlite.db')
    cur = conn.cursor()
    # Fetch item details including names
    cur.execute("SELECT Item_ID, Item_Name, Price FROM Items")
    items = {item[0]: {'name': item[1], 'price': item[2]} for item in cur.fetchall()}

    # Fetch quantities for each item
    cur.execute("SELECT Item_ID, SUM(Quantity) as"
                " TotalQuantity FROM Inventory GROUP BY Item_ID")
    quantities = {row[0]: row[1] for row in cur.fetchall()}
    print(quantities)
    conn.close()
class Cart:
    def __init__(self):
        # Each item in the cart is stored as {item_id: {'quantity': quantity, 'name': name, 'price': price}}
        self.items = {}
        self.cart_count=0

    def add_item(self, item_id, quantity, name, price):
        global quantities  # Ensure you are using the global quantities dictionary
        item_id=int(item_id)

        # Check if adding the item exceeds available quantity
        if quantities.get(item_id, 0) == 0:
            return False, "Not enough stock"
        elif  quantities.get(item_id) >0:
            if item_id in self.items:
                self.items[item_id]['quantity'] += quantity
            else:
                self.items[item_id] = {'quantity': quantity, 'name': name, 'price': price}

            self.cart_count += quantity
            quantities[item_id] -= quantity

            #
            return True, "Item added to cart"

    def calculate_total(self):
        # Calculate the total cost of items in the cart
        return sum(item['price'] * item['quantity'] for item in self.items.values())

    def check_out(self):
        # Process the checkout and update inventory
        try:
            conn = sqlite3.connect('vending_machines_DB.sqlite.db')
            cur = conn.cursor()

            for item_id, details in self.items.items():
                decrease_inventory(item_id, details['quantity'], conn, cur)

            # Record the transaction in Transaction_History
            purchase_total = self.calculate_total()
            purchase_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
            cur.execute("INSERT INTO Transaction_History (VM_ID, Purchase_total, Purchase_Date) VALUES (?, ?, ?)",
                        (VM_ID, purchase_total, purchase_date))

            # Commit changes and clear the cart
            conn.commit()
            self.clear_cart()

            conn.close()
            return True, "Checkout successful"
        except sqlite3.Error as e:
            conn.close()
            return False, str(e)



    def clear_cart(self):
        # Clear all items in the cart
        self.items.clear()
        self.cart_count=0
        get_items()
# Initialize the cart
cart = Cart()
def decrease_inventory(item_id, quantity, conn, cur):
    # Decrease the inventory quantity after dispensing an item
    cur.execute("UPDATE Inventory SET Quantity = Quantity - ? WHERE Item_ID = ?", (quantity, item_id))


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.json
    item_id = data['item_id']
    quantity = data['quantity']
    name = data['name']
    price = data['price']

    success, message = cart.add_item(item_id, quantity, name, price)
    return jsonify(success=success, message=message)


@app.route('/item_quantity/<int:item_id>')
def get_item_quantity(item_id):
    global quantities
    quantity = quantities.get(item_id, 0)
    return jsonify(quantity=quantity)
@app.route('/cart_count')
def get_cart_count():
    return jsonify(cart_count=cart.cart_count)


@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    # Logic to remove item from cart and update quantities
    if item_id in cart.items:
        removed_quantity = cart.items[item_id]['quantity']
        quantities[item_id] += removed_quantity
        del cart.items[item_id]
        cart.cart_count -= removed_quantity
        return jsonify(success=True)
    return jsonify(success=False, message="Item not found in cart")
@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    # Logic to clear the cart and restore quantities
    for item_id, item in cart.items.items():
        quantities[item_id] += item['quantity']
    cart.clear_cart()
    return jsonify(success=True)

@app.route('/pay_with_cash', methods=['POST'])
def pay_with_cash():
    # Process cash payment
    data = request.json
    inserted_amount = float(data['inserted_amount'])
    total_cost = cart.calculate_total()

    if inserted_amount < total_cost:
        return jsonify(success=False, message="Insufficient funds"), 400

    # Connect to the database
    conn = sqlite3.connect('vending_machines_DB.sqlite.db')
    cur = conn.cursor()

    # Check the till for sufficient change
    cur.execute("SELECT Till FROM VM WHERE VM_ID = ?", (VM_ID,))  # Assuming VM_ID is a global variable
    till_amount = cur.fetchone()[0]

    change_needed = inserted_amount - total_cost
    if change_needed > till_amount:
        conn.close()
        return jsonify(success=False, message="Insufficient change in the till. Sorry!"), 400

    # Process the transaction
    success, message = cart.check_out()
    if success:
        # Update the till in the VM table
        new_till_amount = till_amount - change_needed
        cur.execute("UPDATE VM SET Till = ? WHERE VM_ID = ?", (new_till_amount, VM_ID))
        conn.commit()
        conn.close()
        return jsonify(success=True, change=change_needed)
    else:
        conn.close()
        return jsonify(success=False, message=message), 500

@app.route('/pay_with_card', methods=['POST'])
def pay_with_card():
    # Process card payment
    data = request.json
    card_details = data['card_details']  # Placeholder for card details
    total_cost = cart.calculate_total()

    payment_approved = process_card_payment(card_details, total_cost)  # Assuming a function for card payment

    if payment_approved:
        success, message = cart.check_out()
        if success:
            return jsonify(success=True, message="Payment successful")
        else:
            return jsonify(success=False, message=message), 500
    else:
        return jsonify(success=False, message="Card payment failed"), 400

def process_card_payment(card_details, amount):
    # Placeholder function for processing card payment
    return True  # Assume payment is always successful for simulation

@app.route('/checkout')
def checkout():
    global items, quantities
    get_items()  # Refresh items and quantities
    return render_template('checkout.html', cart=cart, items=items)

def get_mysql_connection():
    with open('config.json') as config_file:
        config = json.load(config_file)

    mysql_conn = mysql.connector.connect(
        host=config["host"],
        user=config["mysql_user"],
        password=config["mysql_password"],
        database=config["database"]
    )
    return mysql_conn
@app.route('/login')
def login():
    return render_template('login.html')
@app.route('/login_submit', methods=['POST'])
def login_submit():

    employee_id = request.json['employee_id']
    password = request.json['password']

    mysql_conn = get_mysql_connection()
    mysql_cursor = mysql_conn.cursor()

    # Query the MySQL database
    query = "SELECT * FROM Employee WHERE ID = %s AND Password = %s"
    mysql_cursor.execute(query, (employee_id, password))
    employee = mysql_cursor.fetchone()

    # Close MySQL connection
    mysql_cursor.close()
    mysql_conn.close()

    if employee:
        # Return success response
        return jsonify({'success': True})
    else:
        # Return failure response
        return jsonify({'success': False, 'message': 'Login failed. Please try again.'})


@app.route('/restocker')
def restocker():

    return render_template('restocker.html')


@app.route('/restocker-2')
def restocker_2():

    from restocker import get_low_stock_items,get_expired_items,get_instructions
    low_stock_items=get_low_stock_items(quantities,items,Max_Quantity)
    expired_items=get_expired_items()
    instructions=get_instructions(VM_ID)

    return render_template('restocker-2.html', low_stock_items=low_stock_items,expired_items=expired_items,instructions=instructions)


@app.route('/remove_expired_items', methods=['POST'])
def remove_expired_items():
    items_to_remove = request.form.getlist('item_to_remove')
    with sqlite3.connect('vending_machines_DB.sqlite.db') as conn:
        cur = conn.cursor()
        for item in items_to_remove:
            item_id, expiration_date = item.split('_')
            cur.execute("DELETE FROM Inventory WHERE Item_ID = ? AND Expiration_Date = ?", (item_id, expiration_date))
        conn.commit()
    return jsonify(message="Selected items removed successfully")

@app.route('/restock_items', methods=['POST'])
def restock_items():
    global VM_ID, Max_Quantity
    items_to_restock = request.form.getlist('item_to_restock')
    vm_id = VM_ID
    Max_Items = Max_Quantity

    with sqlite3.connect('vending_machines_DB.sqlite.db') as conn:
        cur = conn.cursor()

        for item_value in items_to_restock:
            item_id, _ = item_value.split('_')  # Split but ignore the second part

            # Check current total quantity for the item
            cur.execute("SELECT SUM(Quantity) FROM Inventory WHERE Item_ID = ?", (item_id,))
            current_quantity = cur.fetchone()[0] or 0

            # Calculate the quantity needed to reach Max_Items
            quantity_needed = Max_Items - current_quantity
            if quantity_needed <= 0:
                continue  # Skip if no restocking is needed

            # Fetch Shelf_Life from Items table
            cur.execute("SELECT Shelf_Life FROM Items WHERE Item_ID = ?", (item_id,))
            shelf_life = cur.fetchone()[0]

            # Calculate Expiration_Date
            expiration_date = (datetime.datetime.now() + datetime.timedelta(weeks=shelf_life)).date()

            # Insert into Inventory
            cur.execute("""
                INSERT INTO Inventory (VM_ID, Item_ID, Quantity, Stock_Date, Expiration_Date) 
                VALUES (?, ?, ?, ?, ?)
                """, (vm_id, item_id, quantity_needed, datetime.datetime.now().date(), expiration_date))

        conn.commit()

    return jsonify(message="Selected items restocked successfully")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=DB_updater.transfer_data(vm_id=VM_ID), trigger="interval",  hours=12)
    scheduler.start()
@app.route('/')
def main_page():
    global item_ids, items, quantities
    get_items()
    item_ids = list(items.keys())
    return render_template('index.html', items=items, quantities=quantities, item_ids=item_ids)


if __name__ == '__main__':
    start_scheduler()
    app.run(debug=True)



