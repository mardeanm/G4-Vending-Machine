
# Flask Vending Machine Application

This Flask application simulates a vending machine's backend, handling the inventory, cart, and payment processes.

## Key Components

### Cart Class
- Represents a user's shopping cart.
- Methods to add items, calculate the total, check out (which includes inventory update), and clear the cart.

### Inventory Update
- Function `decrease_inventory` updates the SQLite database to reduce inventory quantities after items are dispensed.

### Endpoints
- `/add_to_cart`: Adds items to the user's cart. Expects `item_id`, `quantity`, `name`, and `price` in the request JSON.
- `/pay_with_cash`: Handles cash payments. Expects `inserted_amount` in the request JSON. It checks if the amount is sufficient, processes the payment, and updates the inventory.
- `/pay_with_card`: Handles card payments. Expects `card_details` in the request JSON. It simulates card payment processing and updates the inventory upon successful payment.

### Payment Processing
- Cash payments are processed directly based on the amount received.
- Card payments are simulated using the `process_card_payment` function, which always returns success for this demo.

## Usage

1. Start the Flask application by running `python app.py`.
2. Use the provided endpoints to interact with the vending machine system.

Note: This application is a simulation and should be modified for real-world payment processing and security enhancements.
