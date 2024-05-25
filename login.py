from flask import Flask, render_template, request, redirect, url_for, flash
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/yourdbname"
mongo = PyMongo(app)

@app.route('/')
def index():
    return "Welcome to the Flask App"

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        flash('Passwords do not match!')
        return redirect(url_for('index'))
    
    hashed_password = generate_password_hash(password)
    
    # Check if user exists
    existing_user = mongo.db.users.find_one({'email': email})
    if existing_user:
        flash('Email already exists')
        return redirect(url_for('index'))
    
    mongo.db.users.insert_one({'email': email, 'password': hashed_password})
    flash('You have successfully signed up!')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    
    user = mongo.db.users.find_one({'email': email})
    
    if user and check_password_hash(user['password'], password):
        flash('Login successful!')
        return redirect(url_for('index'))
    else:
        flash('Invalid email or password')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
