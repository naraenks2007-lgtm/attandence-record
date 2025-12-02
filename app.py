from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_NAME = "attendance.db"

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Students table to store roll number, name, and current percentage
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                roll_no TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                percentage REAL DEFAULT 100.0
            )
        ''')
        # Logs table to store leave/attendance history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT,
                type TEXT, -- 'LEAVE' or 'ATTEND'
                date TEXT,
                reason TEXT,
                change REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (roll_no) REFERENCES students (roll_no)
            )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/leave', methods=['POST'])
def submit_leave():
    data = request.json
    name = data.get('name')
    roll_no = data.get('roll_no')
    date = data.get('date')
    reason = data.get('reason')

    if not all([name, roll_no, date, reason]):
        return jsonify({"error": "Missing fields"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if student exists, if not create
    cursor.execute('SELECT percentage FROM students WHERE roll_no = ?', (roll_no,))
    student = cursor.fetchone()
    
    if not student:
        current_percentage = 100.0
        cursor.execute('INSERT INTO students (roll_no, name, percentage) VALUES (?, ?, ?)', (roll_no, name, current_percentage))
    else:
        current_percentage = student[0]

    # Calculate new percentage: -3% for leave
    new_percentage = max(0, current_percentage - 3.0) # Ensure doesn't go below 0
    
    # Update student
    cursor.execute('UPDATE students SET percentage = ? WHERE roll_no = ?', (new_percentage, roll_no))
    
    # Log the event
    cursor.execute('INSERT INTO logs (roll_no, type, date, reason, change) VALUES (?, ?, ?, ?, ?)', 
                   (roll_no, 'LEAVE', date, reason, -3.0))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Leave submitted successfully",
        "roll_no": roll_no,
        "new_percentage": round(new_percentage, 2)
    })

@app.route('/api/attend', methods=['POST'])
def mark_attend():
    # This endpoint is for admin/testing to simulate attendance
    data = request.json
    roll_no = data.get('roll_no')
    
    if not roll_no:
        return jsonify({"error": "Missing roll_no"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT percentage FROM students WHERE roll_no = ?', (roll_no,))
    student = cursor.fetchone()
    
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    current_percentage = student[0]
    # Calculate new percentage: +0.3% for attendance
    new_percentage = min(100.0, current_percentage + 0.3) # Ensure doesn't go above 100
    
    cursor.execute('UPDATE students SET percentage = ? WHERE roll_no = ?', (new_percentage, roll_no))
    
    cursor.execute('INSERT INTO logs (roll_no, type, date, reason, change) VALUES (?, ?, ?, ?, ?)', 
                   (roll_no, 'ATTEND', datetime.now().strftime('%Y-%m-%d'), 'Attended Class', 0.3))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Attendance marked",
        "roll_no": roll_no,
        "new_percentage": round(new_percentage, 2)
    })

@app.route('/api/students', methods=['GET'])
def get_students():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students ORDER BY percentage DESC')
    rows = cursor.fetchall()
    students = [dict(row) for row in rows]
    conn.close()
    return jsonify(students)
if _name_ == "_main_":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

