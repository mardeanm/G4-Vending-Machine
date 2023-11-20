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
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

class Cart:
    def __init__(self):
        # Each item in the cart is stored as {item_id: {'quantity': quantity, 'name': name, 'price': price}}
        self.items = {}

    def add_item(self, item_id, quantity, name, price):
        # Add or update an item in the cart
        if item_id in self.items:
            self.items[item_id]['quantity'] += quantity
        else:
            self.items[item_id] = {'quantity': quantity, 'name': name, 'price': price}

    def calculate_total(self):
        # Calculate the total cost of items in the cart
        return sum(item['price'] * item['quantity'] for item in self.items.values())

    def check_out(self):
        # Process the checkout and update inventory
        try:
            for item_id, details in self.items.items():
                decrease_inventory(item_id, details['quantity'])
            self.clear_cart()
            return True, "Checkout successful"
        except sqlite3.Error as e:
            return False, str(e)

    def clear_cart(self):
        # Clear all items in the cart
        self.items.clear()

def decrease_inventory(item_id, quantity):
    # Decrease the inventory quantity after dispensing an item
    conn = sqlite3.connect('vending_machines_DB.sqlite.db')
    cur = conn.cursor()
    cur.execute("UPDATE Inventory SET Quantity = Quantity - ? WHERE Item_ID = ?", (quantity, item_id))
    conn.commit()
    conn.close()

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    # Add items to the cart
    data = request.json
    item_id = data['item_id']
    quantity = data['quantity']
    name = data['name']  # Assuming name is provided in request
    price = data['price']  # Assuming price is provided in request

    cart.add_item(item_id, quantity, name, price)
    return jsonify(success=True)

@app.route('/pay_with_cash', methods=['POST'])
def pay_with_cash():
    # Process cash payment
    data = request.json
    inserted_amount = data['inserted_amount']
    total_cost = cart.calculate_total()

    if inserted_amount >= total_cost:
        success, message = cart.check_out()
        if success:
            change = inserted_amount - total_cost
            return jsonify(success=True, change=change)
        else:
            return jsonify(success=False, message=message), 500
    else:
        return jsonify(success=False, message="Insufficient funds"), 400

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

# Initialize the cart
cart = Cart()

if __name__ == '__main__':
    app.run(debug=True)


# ... (Your existing code for scheduling expiration updates)

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
