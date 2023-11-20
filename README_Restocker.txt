
# Restocker Module for Flask Vending Machine Application

The `restocker.py` module is a part of the Flask vending machine application. It provides functionality for restocking the items in the vending machine.

## Key Functions

### `update_inventory(item_id, quantity)`
- Connects to the SQLite database `vending_machines_DB.sqlite.db`.
- Checks if the item with the given `item_id` exists in the inventory.
- If the item exists, updates its quantity. If it doesn't exist, inserts the new item with the specified quantity into the inventory.
- Commits the changes to the database and closes the connection.

### `restock()`
- Expects a JSON request with `item_id` and `quantity`.
- Calls the `update_inventory` function to update or insert the item in the inventory.
- Returns a JSON response indicating success or failure of the operation.

## Usage

This module is designed to be imported into the main Flask application. It provides an endpoint for restocking items in the vending machine:

- Endpoint: `/restock`
- Method: POST
- Data required: JSON payload with `item_id` and `quantity`.

Example of JSON payload:
```json
{
    "item_id": "123",
    "quantity": 10
}
```

Upon a successful update, it returns a success message; if there's an error, it returns an error message.

Note: This module is part of a larger Flask application and depends on the Flask framework and SQLite database.
