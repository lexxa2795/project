from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'
CORS(app)

# Database initialization
def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect('exam_system.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Exams table
    c.execute('''
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            duration INTEGER NOT NULL,
            total_marks INTEGER NOT NULL,
            created_by INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
    ''')
    
    # Questions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            marks INTEGER DEFAULT 1,
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE
        )
    ''')
    
    # Student Answers table
    c.execute('''
        CREATE TABLE IF NOT EXISTS student_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            student_answer TEXT,
            is_correct BOOLEAN,
            marks_obtained INTEGER DEFAULT 0,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
        )
    ''')
    
    # Exam Results table
    c.execute('''
        CREATE TABLE IF NOT EXISTS exam_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_id INTEGER NOT NULL,
            student_id INTEGER NOT NULL,
            total_marks INTEGER,
            obtained_marks INTEGER,
            percentage REAL,
            status TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (exam_id) REFERENCES exams(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# Decorator for login required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator for admin required
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        
        conn = sqlite3.connect('exam_system.db')
        c = conn.cursor()
        c.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
        result = c.fetchone()
        conn.close()
        
        if result is None or result[0] != 'admin':
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        user = get_user(session['user_id'])
        if user[3] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        conn = sqlite3.connect('exam_system.db')
        c = conn.cursor()
        c.execute('SELECT id, password, role FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()
        
        if result and result[1] == password:  # In production, use proper password hashing
            session['user_id'] = result[0]
            session['username'] = username
            session['role'] = result[2]
            return jsonify({'success': True, 'role': result[2]})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student')
        
        conn = sqlite3.connect('exam_system.db')
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)',
                     (username, email, password, role))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Registration successful'})
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin-dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin_dashboard.html')

@app.route('/student-dashboard')
@login_required
def student_dashboard():
    return render_template('student_dashboard.html')

# API Routes for Admin
@app.route('/api/exams', methods=['GET', 'POST'])
@admin_required
def manage_exams():
    if request.method == 'POST':
        data = request.get_json()
        conn = sqlite3.connect('exam_system.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO exams (title, description, duration, total_marks, created_by, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data['title'], data['description'], data['duration'], data['total_marks'], 
              session['user_id'], 'active'))
        
        exam_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'exam_id': exam_id})
    
    else:  # GET
        conn = sqlite3.connect('exam_system.db')
        c = conn.cursor()
        c.execute('''
            SELECT id, title, description, duration, total_marks, status, created_at
            FROM exams WHERE created_by = ?
        ''', (session['user_id'],))
        
        exams = [{
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'duration': row[3],
            'total_marks': row[4],
            'status': row[5],
            'created_at': row[6]
        } for row in c.fetchall()]
        
        conn.close()
        return jsonify(exams)

@app.route('/api/exams/<int:exam_id>/questions', methods=['GET', 'POST'])
@admin_required
def manage_questions(exam_id):
    if request.method == 'POST':
        data = request.get_json()
        conn = sqlite3.connect('exam_system.db')
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO questions 
            (exam_id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (exam_id, data['question_text'], data['option_a'], data['option_b'],
              data['option_c'], data['option_d'], data['correct_answer'], data.get('marks', 1)))
        
        conn.commit()
        question_id = c.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'question_id': question_id})
    
    else:  # GET
        conn = sqlite3.connect('exam_system.db')
        c = conn.cursor()
        c.execute('''
            SELECT id, question_text, option_a, option_b, option_c, option_d, correct_answer, marks
            FROM questions WHERE exam_id = ?
        ''', (exam_id,))
        
        questions = [{
            'id': row[0],
            'question_text': row[1],
            'option_a': row[2],
            'option_b': row[3],
            'option_c': row[4],
            'option_d': row[5],
            'correct_answer': row[6],
            'marks': row[7]
        } for row in c.fetchall()]
        
        conn.close()
        return jsonify(questions)

# API Routes for Students
@app.route('/api/available-exams', methods=['GET'])
@login_required
def get_available_exams():
    conn = sqlite3.connect('exam_system.db')
    c = conn.cursor()
    
    # Get all active exams that student hasn't completed
    c.execute('''
        SELECT DISTINCT e.id, e.title, e.description, e.duration, e.total_marks
        FROM exams e
        WHERE e.status = 'active'
        AND e.id NOT IN (
            SELECT exam_id FROM exam_results WHERE student_id = ?
        )
    ''', (session['user_id'],))
    
    exams = [{
        'id': row[0],
        'title': row[1],
        'description': row[2],
        'duration': row[3],
        'total_marks': row[4]
    } for row in c.fetchall()]
    
    conn.close()
    return jsonify(exams)

@app.route('/api/exam/<int:exam_id>/start', methods=['GET'])
@login_required
def start_exam(exam_id):
    conn = sqlite3.connect('exam_system.db')
    c = conn.cursor()
    
    # Get exam details
    c.execute('SELECT id, title, duration, total_marks FROM exams WHERE id = ?', (exam_id,))
    exam = c.fetchone()
    
    if not exam:
        conn.close()
        return jsonify({'success': False, 'message': 'Exam not found'}), 404
    
    # Get questions
    c.execute('''
        SELECT id, question_text, option_a, option_b, option_c, option_d, marks
        FROM questions WHERE exam_id = ?
    ''', (exam_id,))
    
    questions = [{
        'id': row[0],
        'question_text': row[1],
        'options': {'A': row[2], 'B': row[3], 'C': row[4], 'D': row[5]},
        'marks': row[6]
    } for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'exam': {
            'id': exam[0],
            'title': exam[1],
            'duration': exam[2],
            'total_marks': exam[3]
        },
        'questions': questions
    })

@app.route('/api/exam/<int:exam_id>/submit', methods=['POST'])
@login_required
def submit_exam(exam_id):
    data = request.get_json()
    answers = data.get('answers')  # Dict of {question_id: answer}
    
    conn = sqlite3.connect('exam_system.db')
    c = conn.cursor()
    
    # Get exam details
    c.execute('SELECT total_marks FROM exams WHERE id = ?', (exam_id,))
    exam = c.fetchone()
    
    if not exam:
        conn.close()
        return jsonify({'success': False, 'message': 'Exam not found'}), 404
    
    total_marks = exam[0]
    obtained_marks = 0
    
    # Process each answer
    for question_id, student_answer in answers.items():
        question_id = int(question_id)
        
        # Get correct answer and marks
        c.execute('SELECT correct_answer, marks FROM questions WHERE id = ? AND exam_id = ?',
                 (question_id, exam_id))
        question = c.fetchone()
        
        if question:
            correct_answer = question[0]
            marks = question[1]
            is_correct = student_answer == correct_answer
            marks_obtained = marks if is_correct else 0
            
            if is_correct:
                obtained_marks += marks_obtained
            
            # Save student answer
            c.execute('''
                INSERT INTO student_answers 
                (exam_id, student_id, question_id, student_answer, is_correct, marks_obtained)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (exam_id, session['user_id'], question_id, student_answer, is_correct, marks_obtained))
    
    # Calculate percentage and status
    percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
    status = 'Pass' if percentage >= 40 else 'Fail'  # 40% is passing
    
    # Save exam result
    c.execute('''
        INSERT INTO exam_results (exam_id, student_id, total_marks, obtained_marks, percentage, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (exam_id, session['user_id'], total_marks, obtained_marks, percentage, status))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'total_marks': total_marks,
        'obtained_marks': obtained_marks,
        'percentage': round(percentage, 2),
        'status': status
    })

@app.route('/api/exam/<int:exam_id>/results', methods=['GET'])
@login_required
def get_exam_results(exam_id):
    conn = sqlite3.connect('exam_system.db')
    c = conn.cursor()
    
    # Get result for current student
    c.execute('''
        SELECT total_marks, obtained_marks, percentage, status, submitted_at
        FROM exam_results WHERE exam_id = ? AND student_id = ?
    ''', (exam_id, session['user_id']))
    
    result = c.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'success': False, 'message': 'No results found'}), 404
    
    # Get detailed answers
    c.execute('''
        SELECT q.question_text, q.correct_answer, sa.student_answer, sa.is_correct, sa.marks_obtained, q.marks
        FROM student_answers sa
        JOIN questions q ON sa.question_id = q.id
        WHERE sa.exam_id = ? AND sa.student_id = ?
    ''', (exam_id, session['user_id']))
    
    answers = [{
        'question': row[0],
        'correct_answer': row[1],
        'student_answer': row[2],
        'is_correct': bool(row[3]),
        'marks_obtained': row[4],
        'total_marks': row[5]
    } for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({
        'success': True,
        'total_marks': result[0],
        'obtained_marks': result[1],
        'percentage': result[2],
        'status': result[3],
        'submitted_at': result[4],
        'answers': answers
    })

@app.route('/api/my-results', methods=['GET'])
@login_required
def get_my_results():
    conn = sqlite3.connect('exam_system.db')
    c = conn.cursor()
    
    c.execute('''
        SELECT e.title, r.total_marks, r.obtained_marks, r.percentage, r.status, r.submitted_at
        FROM exam_results r
        JOIN exams e ON r.exam_id = e.id
        WHERE r.student_id = ?
        ORDER BY r.submitted_at DESC
    ''', (session['user_id'],))
    
    results = [{
        'exam_title': row[0],
        'total_marks': row[1],
        'obtained_marks': row[2],
        'percentage': row[3],
        'status': row[4],
        'submitted_at': row[5]
    } for row in c.fetchall()]
    
    conn.close()
    return jsonify(results)

def get_user(user_id):
    conn = sqlite3.connect('exam_system.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    return user

if __name__ == '__main__':
    app.run(debug=True, port=5000)
