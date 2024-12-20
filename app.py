from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'gamedb'
app.config['MYSQL_PORT'] = 3306  

mysql = MySQL(app)

# --- Route for Signup Page ---
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Get form data
        firstname = request.form['firstname']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat-password']

        if password != repeat_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))
        # Check if email already exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            flash('Email is already registered!', 'error')
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (firstname, email, password) VALUES (%s, %s, %s)', 
                           (firstname, email, hashed_password))
            mysql.connection.commit()
            session['loggedin'] = True
            session['id'] = cursor.lastrowid
            session['username'] = firstname
            flash('You have successfully signed up!', 'success')
            return redirect(url_for('home'))
    return render_template('signup.html')
# --- Route for Home Page ---
@app.route('/')
@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    else:
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('signup'))

# --- Route for Game Page ---
# filepath: /d:/ClassWork/data_structure/GuessGame/GuessGame/app.py
@app.route('/game', methods=['POST'])
def game():
    if 'loggedin' in session:
        category = request.form['category']
        difficulty = request.form['difficulty']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if category == 'Random' and difficulty == 'Random':
            cursor.execute('SELECT word, difficulty, hint FROM word ORDER BY RAND() LIMIT 100')
        elif category == 'Random':
            cursor.execute('SELECT word, difficulty, hint FROM word WHERE difficulty = %s ORDER BY RAND() LIMIT 50', (difficulty,))
        elif difficulty == 'Random':
            cursor.execute('SELECT word, difficulty, hint FROM word WHERE category = %s ORDER BY RAND() LIMIT 50', (category,))
        else:
            cursor.execute('SELECT word, difficulty, hint FROM word WHERE category = %s AND difficulty = %s ORDER BY RAND() LIMIT 50', 
                           (category, difficulty))
        
        words = cursor.fetchall()
        
        if words:
            session['words'] = words  # Store the words in the session
        else:
            flash('No words found for the selected category and difficulty.', 'error')
            return redirect(url_for('home'))
        
        return render_template('game.html', words=words)
    else:
        flash('Please log in to start a game.', 'error')
        return redirect(url_for('signup'))

@app.route('/save_score', methods=['POST'])
def save_score():
    if 'loggedin' in session:
        user_id = session['id']
        data = request.json
        score = data.get('score', 0)  # Get the final score from frontend
        guessed_words = data.get('guessedWords', [])
        word_count = len(guessed_words)
        
        for word in guessed_words:
            score += int(word['points'])
    
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
        cursor.execute('INSERT INTO score (user_id, score, guesses) VALUES (%s, %s, %s)', (user_id, score, word_count))
        
        mysql.connection.commit()
        return {'message': 'Score saved successfully!'}, 200
    else:
        return {'error': 'User not logged in!'}, 401

# --- Route for Login Page ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user['password'], password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['firstname']
            flash('You have successfully logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Incorrect email or password!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/leader')
def leader():
    if 'loggedin' in session:
        user_id = session['id']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Retrieve top 10 leaderboard scores without summing
        cursor.execute("""
            SELECT users.firstname AS player_name, score.score, score.guesses 
            FROM users 
            JOIN score ON users.id = score.user_id 
            ORDER BY score.score DESC
            LIMIT 10
        """)
        leaderboard = cursor.fetchall()
        
        # Retrieve current user's last score
        cursor.execute("""
            SELECT score, guesses 
            FROM score 
            WHERE user_id = %s 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (user_id,))
        last_score = cursor.fetchone()
        
        return render_template('leader.html', leaderboard=leaderboard, last_score=last_score, username=session['username'], enumerate=enumerate)
    else:
        flash('Please log in to view the leaderboard.', 'error')
        return redirect(url_for('signup'))  

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('signup'))

@app.route('/next_word', methods=['POST', 'GET'])
def next_word():
    if 'loggedin' in session:
        data = request.json
        guessed_words = data.get('guessedWords', [])
        
        category = session.get('category', 'Random')
        difficulty = session.get('difficulty', 'Random')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if guessed_words:
            query = 'SELECT word FROM word WHERE word NOT IN (%s)' % ','.join(['%s'] * len(guessed_words))
            params = guessed_words
        else:
            query = 'SELECT word FROM word'
            params = []
        
        if category != 'Random':
            query += ' AND category = %s'
            params.append(category)
        
        if difficulty != 'Random':
            query += ' AND difficulty = %s'
            params.append(difficulty)
        
        query += ' ORDER BY RAND() LIMIT 1'
        
        cursor.execute(query, params)
        word_entry = cursor.fetchone()
        
        if word_entry:
            word_to_guess = word_entry['word']
            return {'success': True, 'word': word_to_guess}
        else:
            return {'success': False, 'message': 'No more words available for the selected category and difficulty.'}
    else:
        return {'error': 'User not logged in!'}, 401

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5000, debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)

