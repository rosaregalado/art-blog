from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import bcrypt

host = os.environ.get('MONGODB_URI')
client = MongoClient(host)
db = client.ecommerce_app

# db resources
users = db.users
items = db.items


app = Flask(__name__)

# ----------------------------------------------------------
# users routes

@app.route('/')
def index():
  if 'username' in session:
    # return 'You are logged in as ' + session['username']
    return redirect(url_for('profile'))



@app.route('/register', methods=['POST', 'GET'])
def register():
  if request.method == 'POST':
    existing_user = users.find_one({'name': request.form['username']})

    if existing_user is None:
      hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8') , bcrypt.gensalt())
      users.insert({'name': request.form['username'], 'password': hashpass})
      # create session
      session['username'] = request.form['username']
      return redirect(url_for('index'))

    return 'That username already exists!'
  # else request.method=GET
  return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
  login_user = users.find_one({'name': request.form['username']})

  if login_user:
    # checks if passwords are same
    if bcrypt.hashpw(request.form['pass'], login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
      # add user to session
      session['username'] = request.form['username']
      return redirect(url_for('login_index'))

  # if password is wrong or username doesnt exist
  return 'Invalid username/password combination'

@app.route('/logout')
def logout():
  session['username'] = None
  session['password'] = None
  
  return redirect(url_for('login'))
# ----------------------------------------------------------
# other routes

@app.route('/profile')
def profile():
  return render_template('profile.html')

@app.route('/inspiration')
def inspiration():
  return render_template('inspiration.html')

@app.route('/poems')
def poems():
  return render_template('poems.html')

@app.route('/stories')
def stories():
  return render_template('stories.html')






if __name__ == "__main__":
  app.secret_key = 'mysecret'
  app.run(debug=True)