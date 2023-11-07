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


from flask import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', name="Vending")


if __name__ == '__main__':
    app.run()
