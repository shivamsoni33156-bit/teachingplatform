"""
Coaching Institute Website - Flask Backend
IIT/NEET Success - Professional Coaching Institute
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import sqlite3
import os
import random
from datetime import datetime
import hashlib

app = Flask(__name__)
app.secret_key = 'gravity_coaching_secret_key_2024'

# Database configuration
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def init_db():
    """Initialize database with tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Courses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            duration TEXT,
            price INTEGER,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Enrollments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            payment_status TEXT DEFAULT 'pending',
            progress INTEGER DEFAULT 0,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    ''')
    
    # Study materials table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS study_materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            video_url TEXT,
            pdf_path TEXT,
            chapter_number INTEGER,
            FOREIGN KEY (course_id) REFERENCES courses(id)
        )
    ''')
    
    # OTP verification table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_verify (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            otp TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP DEFAULT (datetime('now', '+5 minutes'))
        )
    ''')
    
    # Insert default courses if not exist
    cursor.execute('SELECT COUNT(*) FROM courses')
    if cursor.fetchone()[0] == 0:
        courses = [
            ('JEE Preparation', 'Comprehensive JEE Main & Advanced preparation with expert faculty', '2 Years', 150000, 'jee.jpg'),
            ('NEET Preparation', 'Complete NEET UG preparation with mock tests and study materials', '2 Years', 140000, 'neet.jpg'),
            ('Engineering Entrance', 'State-level engineering entrance exam preparation', '1 Year', 80000, 'engineering.jpg'),
            ('BCA Preparation', 'BCA entrance exam preparation for top colleges', '6 Months', 40000, 'bca.jpg')
        ]
        cursor.executemany('INSERT INTO courses (title, description, duration, price, image) VALUES (?, ?, ?, ?, ?)', courses)
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

# Routes
@app.route('/')
def index():
    """Homepage route"""
    conn = get_db_connection()
    courses = conn.execute('SELECT * FROM courses LIMIT 4').fetchall()
    conn.close()
    return render_template('index.html', courses=courses)

@app.route('/courses')
def courses():
    """Courses page"""
    conn = get_db_connection()
    courses = conn.execute('SELECT * FROM courses').fetchall()
    conn.close()
    return render_template('courses.html', courses=courses)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login and registration page"""
    if request.method == 'POST':
        action = request.form.get('action')
        phone = request.form.get('phone')
        
        if action == 'send_otp':
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Delete old OTPs for this phone
            cursor.execute('DELETE FROM otp_verify WHERE phone = ?', (phone,))
            
            # Insert new OTP
            cursor.execute('INSERT INTO otp_verify (phone, otp) VALUES (?, ?)', (phone, otp))
            conn.commit()
            conn.close()
            
            # In production, send OTP via SMS gateway
            # For demo, return OTP in response
            session['phone'] = phone
            session['otp_sent'] = True
            return jsonify({'success': True, 'message': f'OTP sent! (Demo: {otp})'})
        
        elif action == 'verify_otp':
            otp = request.form.get('otp')
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verify OTP
            result = cursor.execute('SELECT * FROM otp_verify WHERE phone = ? AND otp = ? AND expires_at > datetime("now")', 
                                   (phone, otp)).fetchone()
            
            if result:
                # Check if user exists
                user = cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
                if not user:
                    # Create new user
                    name = request.form.get('name', 'Student')
                    password = hash_password(phone)  # Default password is phone number
                    cursor.execute('INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)',
                                  (name, f'{phone}@gravity.com', phone, password))
                    user = cursor.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
                
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['is_admin'] = user['is_admin']
                
                # Clean up OTP
                cursor.execute('DELETE FROM otp_verify WHERE phone = ?', (phone,))
                conn.commit()
                conn.close()
                
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            else:
                conn.close()
                return jsonify({'success': False, 'message': 'Invalid or expired OTP'})
        
        elif action == 'login_password':
            # Traditional login with password
            password = hash_password(request.form.get('password'))
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE phone = ? AND password = ?', 
                               (phone, password)).fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['is_admin'] = user['is_admin']
                return jsonify({'success': True, 'redirect': url_for('dashboard')})
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Student dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    enrollments = conn.execute('''
        SELECT e.*, c.title, c.description, c.duration, c.price, c.image
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.user_id = ?
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('dashboard.html', user=user, enrollments=enrollments)

@app.route('/payment/<int:course_id>', methods=['GET', 'POST'])
def payment(course_id):
    """Payment page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    course = conn.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    
    if request.method == 'POST':
        payment_method = request.form.get('payment_method')
        
        # Simulate payment processing
        # In production, integrate with Razorpay/PayU
        
        # Create enrollment
        conn.execute('INSERT INTO enrollments (user_id, course_id, payment_status, progress) VALUES (?, ?, ?, ?)',
                    (session['user_id'], course_id, 'completed', 0))
        conn.commit()
        conn.close()
        
        return redirect(url_for('dashboard'))
    
    conn.close()
    return render_template('payment.html', course=course)

@app.route('/study_material/<int:course_id>')
def study_material(course_id):
    """Video and study material page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Check if enrolled
    conn = get_db_connection()
    enrollment = conn.execute('SELECT * FROM enrollments WHERE user_id = ? AND course_id = ? AND payment_status = ?',
                             (session['user_id'], course_id, 'completed')).fetchone()
    
    if not enrollment:
        conn.close()
        return redirect(url_for('courses'))
    
    course = conn.execute('SELECT * FROM courses WHERE id = ?', (course_id,)).fetchone()
    materials = conn.execute('SELECT * FROM study_materials WHERE course_id = ? ORDER BY chapter_number',
                            (course_id,)).fetchall()
    conn.close()
    
    return render_template('study_material.html', course=course, materials=materials, enrollment=enrollment)

@app.route('/enroll/<int:course_id>')
def enroll(course_id):
    """Enroll in a course"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return redirect(url_for('payment', course_id=course_id))

# Admin routes
@app.route('/admin')
def admin():
    """Admin panel"""
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    courses = conn.execute('SELECT * FROM courses').fetchall()
    users = conn.execute('SELECT * FROM users WHERE is_admin = 0').fetchall()
    enrollments = conn.execute('''
        SELECT e.*, u.name, u.phone, c.title
        FROM enrollments e
        JOIN users u ON e.user_id = u.id
        JOIN courses c ON e.course_id = c.id
    ''').fetchall()
    conn.close()
    
    return render_template('admin.html', courses=courses, users=users, enrollments=enrollments)

@app.route('/admin/add_course', methods=['POST'])
def admin_add_course():
    """Add new course"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    title = request.form.get('title')
    description = request.form.get('description')
    duration = request.form.get('duration')
    price = request.form.get('price')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO courses (title, description, duration, price) VALUES (?, ?, ?, ?)',
                (title, description, duration, price))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/add_material', methods=['POST'])
def admin_add_material():
    """Add study material"""
    if 'user_id' not in session or not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    course_id = request.form.get('course_id')
    title = request.form.get('title')
    description = request.form.get('description')
    chapter_number = request.form.get('chapter_number')
    
    conn = get_db_connection()
    conn.execute('INSERT INTO study_materials (course_id, title, description, chapter_number) VALUES (?, ?, ?, ?)',
                (course_id, title, description, chapter_number))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# Static files
@app.route('/static/videos/<path:filename>')
def serve_video(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'videos'), filename)

@app.route('/static/pdfs/<path:filename>')
def serve_pdf(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'pdfs'), filename)

# Add template filters
@app.template_filter('format_price')
def format_price(value):
    """Format price with commas"""
    return "{:,}".format(int(value))

# Create admin user
def create_admin():
    conn = get_db_connection()
    admin = conn.execute('SELECT * FROM users WHERE is_admin = 1').fetchone()
    if not admin:
        conn.execute('INSERT INTO users (name, email, phone, password, is_admin) VALUES (?, ?, ?, ?, ?)',
                    ('Admin', 'admin@gravity.com', '9999999999', hash_password('admin123'), 1))
        conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    create_admin()
    app.run(debug=True, port=5000)

