from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'ilovecrab'  

conn = sqlite3.connect('airlines.db', check_same_thread=False)
conn.execute('CREATE TABLE IF NOT EXISTS reservations (reservation_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, flight_id INTEGER, FOREIGN KEY (user_id) REFERENCES users (id), FOREIGN KEY (flight_id) REFERENCES flights (flight_id))')
conn.close()

@app.route('/')
def index():
    return render_template("main.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('airlines.db', check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        existing_user = cursor.fetchone()

        if not existing_user:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            return redirect(url_for('login'))

        conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('airlines.db', check_same_thread=False)
        cursor = conn.cursor()


        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]  
            return redirect(url_for('userdash'))

        conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/userdash')
def userdash():
    if 'user_id' in session:
        username = session['username']
        return render_template('userdash.html', username=username)
    else:
        return redirect(url_for('login'))

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']

        conn = sqlite3.connect('airlines.db', check_same_thread=False)
        cursor = conn.cursor()


        cursor.execute('SELECT * FROM admin WHERE admin_username = ?', (admin_username,))
        existing_admin = cursor.fetchone()

        if not existing_admin:
            cursor.execute('INSERT INTO admin (admin_username, admin_password) VALUES (?, ?)', (admin_username, admin_password))
            conn.commit()
            return redirect(url_for('admin_login'))

        conn.close()

    return render_template('admin_register.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        admin_username = request.form['admin_username']
        admin_password = request.form['admin_password']

        conn = sqlite3.connect('airlines.db', check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM admin WHERE admin_username = ? AND admin_password = ?', (admin_username, admin_password))
        admin = cursor.fetchone()

        if admin:
            session['user_id'] = admin[0]
            session['username'] = admin[1]  
            return redirect(url_for('admin_dash'))

        conn.close()

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/admin_dash')
def admin_dash():
    if 'user_id' in session:
        username = session['username']
        return render_template('admin_dash.html', username=username)
    else:
        return redirect(url_for('admin_login'))

#for Users
@app.route('/flights')
def view_flights_user():
    conn = sqlite3.connect('airlines.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM flights')
    flights = cursor.fetchall()

    conn.close()

    if 'user_id' in session:
        return render_template('view_flights_user.html', flights=flights)
    else:
        return redirect(url_for('index'))  

@app.route('/admin/flights')
def view_flights_admin():
    conn = sqlite3.connect('airlines.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM flights')
    flights = cursor.fetchall()

    conn.close()

    return render_template("view_flights_admin.html", flights=flights) 

@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
    if request.method == 'POST':
        airline_name = request.form['airline_name']
        departure_time = request.form['departure_time']
        capacity = request.form['capacity']

        conn = sqlite3.connect('airlines.db', check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute('INSERT INTO flights (airline_name, departure_time, capacity) VALUES (?, ?, ?)',
                       (airline_name, departure_time, capacity))
        conn.commit()

        conn.close()
        return redirect(url_for('view_flights_admin'))

    return render_template('add_flight.html')

@app.route('/update_flight/<int:flight_id>', methods=['GET', 'POST'])
def update_flight(flight_id):
    conn = sqlite3.connect('airlines.db', check_same_thread=False)
    cursor = conn.cursor()

    if request.method == 'POST':
        airline_name = request.form['airline_name']
        departure_time = request.form['departure_time']
        capacity = request.form['capacity']

        cursor.execute('UPDATE flights SET airline_name=?, departure_time=?, capacity=? WHERE flight_id=?',
                       (airline_name, departure_time, capacity, flight_id))
        conn.commit()

        conn.close()
        return redirect(url_for('view_flights_admin'))

    cursor.execute('SELECT * FROM flights WHERE flight_id=?', (flight_id,))
    flight = cursor.fetchone()

    conn.close()
    return render_template('update_flight.html', flight=flight)

@app.route('/delete_flight/<int:flight_id>')
def delete_flight(flight_id):
    conn = sqlite3.connect('airlines.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM flights WHERE flight_id=?', (flight_id,))
    conn.commit()

    conn.close()
    return redirect(url_for('view_flights'))

@app.route('/reservations')
def view_reservations():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('airlines.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('SELECT reservations.reservation_id, flights.airline_name, flights.departure_time FROM reservations JOIN flights ON reservations.flight_id = flights.flight_id WHERE user_id = ?', (user_id,))
    user_reservations = cursor.fetchall()

    conn.close()
    return render_template('view_reservations.html', user_reservations=user_reservations)

@app.route('/make_reservation/<int:flight_id>')
def make_reservation(flight_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('airlines.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('INSERT INTO reservations (user_id, flight_id) VALUES (?, ?)', (user_id, flight_id))
    conn.commit()

    conn.close()
    return redirect(url_for('view_reservations'))

@app.route('/cancel_reservation/<int:reservation_id>')
def cancel_reservation(reservation_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('airlines.db', check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM reservations WHERE reservation_id = ? AND user_id = ?', (reservation_id, user_id))
    conn.commit()

    conn.close()
    return redirect(url_for('view_reservations'))


app.run(debug=True)
