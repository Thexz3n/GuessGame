from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'gamedb'
app.config['MYSQL_PORT'] = 3306  


mysql = MySQL(app)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        firstname = request.form['firstname']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat-password']

        if password != repeat_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup'))

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (firstname, email, password) VALUES (%s, %s, %s)", (firstname, email, password))
        mysql.connection.commit()
        cursor.close()

        flash('Signup successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/')
def home():
    return render_template('login.html')
if __name__ == '__main__':
    app.run(debug=True)
