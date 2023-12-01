#if not in use standby
#show product options w/ price, quantity available
# adding the items to cart
#check out
#be able to cancel the order

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
from flask import Flask, request, jsonify, render_template
import sqlite3
from apscheduler.schedulers.background import BackgroundScheduler
import DB_updater
import datetime
app = Flask(__name__)

VM_ID=1
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

    conn.close()
class Cart:
    def __init__(self):
        # Each item in the cart is stored as {item_id: {'quantity': quantity, 'name': name, 'price': price}}
        self.items = {}
        self.cart_count=0

    def add_item(self, item_id, quantity, name, price):
        global quantities  # Ensure you are using the global quantities dictionary
        item_id=int(item_id)

        # Debugging: Print current quantities
        # print(f"Current available quantity for item {item_id}: {quantities.get(item_id, 0)}")
        # print(f"Current quantity in cart for item {item_id}: {self.items.get(item_id, {}).get('quantity', 0)}")

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

            # # Debugging: Print updated quantities
            # print(f"Updated available quantity for item {item_id}: {quantities[item_id]}")
            # print(f"Updated quantity in cart for item {item_id}: {self.items[item_id]['quantity']}")
            # print(self.items)
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
@app.route('/item_quantity/<int:item_id>')
def get_item_quantity(item_id):
    global quantities
    quantity = quantities.get(item_id, 0)
    return jsonify(quantity=quantity)
@app.route('/cart_count')
def get_cart_count():
    return jsonify(cart_count=cart.cart_count)
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

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=DB_updater.transfer_data(vm_id=VM_ID), trigger="interval",  hours=12)
    scheduler.start()



@app.route('/checkout')
def checkout():
    global items, quantities
    get_items()  # Refresh items and quantities
    return render_template('checkout.html', cart=cart, items=items)


@app.route('/')
def main_page():
    global item_ids, items, quantities
    get_items()
    item_ids = list(items.keys())
    return render_template('index.html', items=items, quantities=quantities, item_ids=item_ids)
if __name__ == '__main__':
    #start_scheduler()
    app.run(debug=True)



