

# from flask import Flask, render_template, request, redirect, url_for
# import os
# import sqlite3
# from datetime import datetime
# from pytz import timezone

# # Create the Flask app
# app = Flask(__name__)

# # Connect to SQLite database
# def get_db():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row  # Allows accessing columns by name
#     return conn

# # Initialize database with tables and sample data
# def init_db():
#     with get_db() as conn:
#         conn.executescript("""
#             CREATE TABLE IF NOT EXISTS resources (
#                 resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 name TEXT NOT NULL,
#                 category TEXT NOT NULL,
#                 location TEXT,
#                 description TEXT
#             );
#             CREATE TABLE IF NOT EXISTS bookings (
#                 booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 student_name TEXT NOT NULL,
#                 email TEXT NOT NULL,
#                 resource_id INTEGER,
#                 date DATE NOT NULL,
#                 start_time TIME NOT NULL,
#                 end_time TIME NOT NULL,
#                 status TEXT DEFAULT 'Pending',
#                 reason TEXT,
#                 FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
#             );
#             INSERT OR IGNORE INTO resources (name, category, location, description)
#             VALUES ('Seminar Hall A', 'Hall', 'Main Building', 'Seats 100'),
#                    ('Computer Lab 1', 'Lab', 'Tech Block', '40 PCs'),
#                    ('LCD Projector', 'Projector', 'Library', 'Portable');
#         """)
#         conn.commit()

# # Home route (displays homepage)
# @app.route('/')
# def home():
#     return render_template('index.html')

# # Resources route (lists all resources)
# @app.route('/resources')
# def resources():
#     with get_db() as conn:
#         resources = conn.execute('SELECT * FROM resources').fetchall()
#     return render_template('resources.html', resources=resources)

# # Book resources route (handles booking form)
# @app.route('/bookresources', methods=['GET', 'POST'])
# def bookresources():
#     if request.method == 'POST':
#         student_name = request.form['student_name']
#         email = request.form['email']
#         resource_id = request.form['resource_id']
#         date = request.form['date']
#         start_time = request.form['start_time']
#         end_time = request.form['end_time']
#         reason = request.form['reason']
#         with get_db() as conn:
#             conn.execute("""
#                 INSERT INTO bookings (student_name, email, resource_id, date, start_time, end_time, reason)
#                 VALUES (?, ?, ?, ?, ?, ?, ?)
#             """, (student_name, email, resource_id, date, start_time, end_time, reason))
#             conn.commit()
#         return redirect(url_for('booking_status'))
#     with get_db() as conn:
#         resources = conn.execute('SELECT * FROM resources').fetchall()
#     return render_template('bookresources.html', resources=resources)

# # Booking status route (shows user's bookings)
# @app.route('/booking_status')
# def booking_status():
#     email = request.args.get('email', 'test@example.com')  # Temporary, replace with user session
#     with get_db() as conn:
#         bookings = conn.execute("""
#             SELECT b.*, r.name
#             FROM bookings b JOIN resources r ON b.resource_id = r.resource_id
#             WHERE b.email = ? ORDER BY b.date DESC
#         """, (email,)).fetchall()
#     return render_template('booking_status.html', bookings=bookings)

# # Admin route (manages bookings)
# @app.route('/admin', methods=['GET', 'POST'])
# def admin():
#     if request.method == 'POST':
#         booking_id = request.form['booking_id']
#         status = request.form['status']
#         with get_db() as conn:
#             conn.execute('UPDATE bookings SET status = ? WHERE booking_id = ?', (status, booking_id))
#             conn.commit()
#         return redirect(url_for('admin'))
#     with get_db() as conn:
#         bookings = conn.execute("""
#             SELECT b.*, r.name
#             FROM bookings b JOIN resources r ON b.resource_id = r.resource_id
#             ORDER BY b.date DESC
#         """).fetchall()
#     return render_template('administrator.html', bookings=bookings)

# # Run the app
# if __name__ == '__main__':
#     if not os.path.exists('database.db'):
#         init_db()  # Create database and tables if they don't exist
#     port = int(os.environ.get('PORT', 8000))
#     app.run(host='0.0.0.0', port=port, debug=True)



from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import datetime
import os

# Flask app setup
app = Flask(__name__)

# MySQL Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',      # 👈 Replace with your MySQL username
    'password': 'gopi@001',  # 👈 Replace with your MySQL password
    'database': 'college_bookings'   # 👈 Replace with your MySQL database name
}

# Database connection
def get_db():
    return mysql.connector.connect(**db_config)

# Initialize tables and sample data (run only once)
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            resource_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            location VARCHAR(255),
            description TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            resource_id INT,    
            date DATE NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            status VARCHAR(50) DEFAULT 'Pending',
            reason TEXT,
            FOREIGN KEY (resource_id) REFERENCES resources(resource_id)
        )
    """)

    cursor.execute("""
        INSERT IGNORE INTO resources (name, category, location, description)
        VALUES 
        ('Seminar Hall A', 'Hall', 'Main Building', 'Seats 100'),
        ('Computer Lab 1', 'Lab', 'Tech Block', '40 PCs'),
        ('LCD Projector', 'Projector', 'Library', 'Portable')
    """)

    conn.commit()
    cursor.close()
    conn.close()

# Home route
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/resource')
def resource():
    return render_template('resources.html')

# # View resources
# @app.route('/resources')
# def resources():
#     with get_db() as conn:
#         resources = conn.execute('SELECT * FROM resources').fetchall()
#     return render_template('resources.html', resources=resources)

# Book resource
@app.route('/bookresources', methods=['GET', 'POST'])
def bookresources():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = (
            request.form['student_name'],
            request.form['email'],
            int(request.form['resource_id']),  # Ensure resource_id is an integer
            request.form['date'],
            request.form['start_time'],
            request.form['end_time'],
            request.form['reason']
        )
        cursor.execute("""
            INSERT INTO bookings (student_name, email, resource_id, date, start_time, end_time, reason)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, data)
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('booking_status'))

    cursor.execute("SELECT * FROM resources")
    resources = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('bookresources.html', resources=resources)

# Booking status page
@app.route('/booking_status')
def booking_status():
    email = request.args.get('email', 'test@example.com')  # Replace with session/email auth later
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT b.*, r.name AS resource_name
        FROM bookings b
        JOIN resources r ON b.resource_id = r.resource_id
        WHERE b.email = %s
        ORDER BY b.date DESC
    """, (email,))
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('booking_status.html', bookings=bookings)

# Admin dashboard
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
 
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        status = request.form['status']
        cursor.execute("UPDATE bookings SET status = %s WHERE booking_id = %s", (status, booking_id))
        conn.commit()
        return redirect(url_for('admin'))

    cursor.execute("""
        SELECT b.*, r.name AS resource_name
        FROM bookings b
        JOIN resources r ON b.resource_id = r.resource_id
        ORDER BY b.date DESC
    """)
    bookings = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('administrator.html', bookings=bookings)


# Main
if __name__ == '__main__':
    init_db()  # Only needed the first time (comment out later if needed)
    app.run(debug=True, host='0.0.0.0', port=8000)
