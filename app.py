from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

host = os.environ.get('MONGODB_URI')
client = MongoClient(host)
db = client.StockHome

# db resources
items = db.items


app = Flask(__name__)

# ----------------------------------------------------------
#root route
@app.route('/')
def index():
  # home page
  return render_template('index.html', items=items.find())

# show item
@app.route('/items/<item_id>')
def item_show(item_id):
  item = items.find_one({'_id': ObjectId(item_id)})
  return render_template('item.html', item=item)

# create new item
@app.route('/items/new', methods=['POST'])
def new_item():
  item = {
    'item_image': request.form.get('item_image'),
    'item_name': request.form.get('item_name'),
    'item_description': request.form.get('item_description'),
    'item_price': request.form.get('item_price')
  }
  # add item to db
  item_id = items.insert_one(item).inserted_id
  return render_template('new_item.html', item_id=item_id)

# update item
@app.route('/items/<item_id>', methods=['POST'])
def item_update(item_id):
  updated_item = {
    'item_image': request.form.get('item_image'),
    'item_name': request.form.get('item_name'),
    'item_description': request.form.get('item_description'),
    'item_price': request.form.get('item_price')
  }
  # set former item to updated item
  items.update_one(
    {'_id': ObjectId(item_id)},
    {'$set': updated_item}
  )
  return redirect(url_for('items_show', item_id=item_id))

# show all items






if __name__ == "__main__":
  app.run(debug=True)