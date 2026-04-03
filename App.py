from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to something secure

# MongoDB Atlas connection
client = MongoClient("mongodb+srv://<username>:<password>@cluster0.mongodb.net/socialmedia?retryWrites=true&w=majority")
db = client['socialmedia']
users_col = db['users']
posts_col = db['posts']

# Home redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_col.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect(url_for('feed'))
        else:
            return "Invalid login!"
    return render_template('login.html')

# Signup Page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_col.find_one({'username': username}):
            return "User already exists!"
        users_col.insert_one({'username': username, 'password': password})
        return redirect(url_for('login'))
    return render_template('signup.html')

# Profile Page
@app.route('/profile/<username>')
def profile(username):
    user_posts = list(posts_col.find({'username': username}))
    return render_template('profile.html', username=username, posts=user_posts)

# Feed Page
@app.route('/feed', methods=['GET', 'POST'])
def feed():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        content = request.form['content']
        posts_col.insert_one({'username': session['username'], 'content': content})
    all_posts = list(posts_col.find().sort('_id', -1))
    return render_template('feed.html', posts=all_posts)

# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
