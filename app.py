from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import bcrypt
import datetime

host = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/art-blog')
client = MongoClient(host=host)
db = client.art_blog

# db resources
users = db.users
poems = db.poems


app = Flask(__name__)
app.secret_key = 'mysecretnooneknows'

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
      # add to db
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
  return redirect(url_for('index'))

# ---------------------------------------------------------------------------------
# poems routes

@app.route('/poetry')
def poetry():
  return render_template('poetry.html', poems=poems.find())

@app.route('/poetry/new')
def new_poem():
  return render_template('new_poem.html', poem = {}, title="Upload New Poem")

@app.route('/poetry', methods=['POST'])
def submit_poem():
  if 'username' in session:
    poem = {
      'title': request.form.get('title'),
      'poem': request.form.get('poem'),
      'date_created': request.form.get('date_created')
    }
    poem_id = poems.insert_one(poem).inserted_id
    flash("Successfully added a new poem", "success")
    return redirect(url_for('poetry', poem_id=poem_id))
  else:
    flash("You must be logged in to continue", "warning")
    return redirect(url_for('index'))

@app.route('/poems/<poem_id>')
def view_poem(poem_id):
  poem = poems.find_one({'_id': ObjectId(poem_id)})
  return render_template('view_poem.html', poem=poem)

# edit poem
@app.route('/poems/<poem_id>/edit')
def edit_poem(poem_id):
  poem = poems.find_one({'id': ObjectId(poem_id)})
  return render_template('edit_poem.html', poem=poem)

# update poem
@app.route('/poems/<poem_id>', methods=['POST'])
def update_poem(poem_id):
  updated_poem = {
    'title': request.form.get('title'),
    'poem': request.form.get('poem'),
    'date_created': request.form.get('date_created')
  }
  poems.update_one(
    {'_id': ObjectId(poem_id)},
    {'$set': updated_poem}
  )
  # redirect to poetry main page
  return redirect(url_for('view_poetry', poem_id=poem_id))

# delete poem
@app.route('/poems/<poem_id>/delete', methods=['POST'])
def delete_poem(poem_id):
  flash("You deleted a poem!", "danger")
  poems.delete_one({'_id': ObjectId(poem_id)})
  return redirect(url_for('poetry'))

# ----------------------------------------------------------
# other routes

@app.route('/profile')
def profile():
  return render_template('profile.html')

@app.route('/photography')
def photography():
  return render_template('photography.html')

@app.route('/stories')
def stories():
  return render_template('stories.html')


# ----------------------------------------------------------



if __name__ == "__main__":
  app.run(debug=True)
  