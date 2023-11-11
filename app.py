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
from flask import Flask, render_template
import sqlite3
from datetime import datetime, timedelta
app = Flask(__name__)


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


def get_item_prices():
    # Connect to your SQLite database
    conn = sqlite3.connect('vending_machines_DB.sqlite.db')
    cur = conn.cursor()

    # Query the database for item prices
    cur.execute("SELECT item_name, price FROM items")  # Adjust the table and column names as per your DB
    items = cur.fetchall()

    # Close the connection to the database
    conn.close()

    # Convert fetched data into a dictionary
    item_prices = {name: price for name, price in items}
    print(item_prices)
    return item_prices
# @app.route('/')
# def update_expiration_route():
#     update_expiration_dates('vending_machines_DB.sqlite.db')
#     return "Expiration dates updated successfully!"
@app.route('/')
def index():
    # Get the current prices of items from the database
    item_prices = get_item_prices()

    # Pass the prices to the template
    return render_template('index.html', item_prices=item_prices)

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
