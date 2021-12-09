from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import bcrypt

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/art-blog')
client = MongoClient(host=host)
db = client.art_blog

# db resources
users = db.users
poems = db.poems


app = Flask(__name__)

# ----------------------------------------------------------
# users routes

@app.route('/')
def index():
  # if 'username' in session:
    # return 'You are logged in as ' + session['username']
    return render_template('index.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
  if request.method == 'POST':
    existing_user = users.find_one({'name': request.form['username']})

    if existing_user is None:
      # hash password
      hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8') , bcrypt.gensalt())
      users.insert_one({'name': request.form['username'], 'password': hashpass})
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
    if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
      # add user to session
      session['username'] = request.form['username']
      flash("Login successful", "success")
      return redirect(url_for('profile'))

  # if password is wrong or username doesnt exist
  return 'Invalid username/password combination'

@app.route('/logout')
def logout():
  session.pop('username')
  flash("logged out", "warning")
  return redirect(url_for('login'))
# ----------------------------------------------------------
# other routes

@app.route('/profile')
def profile():
  return render_template('profile.html')

@app.route('/photography')
def photography():
  return render_template('photography.html')

@app.route('/poetry')
def poetry():
  return render_template('poetry.html', poems=poems.find())

@app.route('/poetry/new')
def new_poem():
  return render_template('new_poem.html', poem = {}, title="Upload New Poem")

@app.route('/poetry', methods=['POST'])
def submit_poem():
  poem = {
    'title': request.form.get('title'),
    'poem': request.form.get('poem')
  }
  poem_id = poems.insert_one(poem).inserted_id
  flash("Successfully added a new poem", "success")
  return redirect(url_for('poetry', poem_id=poem_id))


@app.route('/stories')
def stories():
  return render_template('stories.html')






if __name__ == "__main__":
  app.secret_key = 'mysecret'
  app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))