from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField, FileField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import random
import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+mysqlconnector://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/videos'
app.config['PDF_FOLDER'] = 'static/pdfs'
db = SQLAlchemy(app)

@app.context_processor
def inject_user():
    if 'user_id' in session:
        return dict(current_user=User.query.get(session['user_id']))
    return dict(current_user=None)

# Models
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    mobile = db.Column(db.String(10), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    desc = db.Column(db.Text)
    duration = db.Column(db.String(50))
    price = db.Column(db.Integer)

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, paid
    progress = db.Column(db.Integer, default=0)

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    chapter = db.Column(db.String(100))
    video_path = db.Column(db.String(200))
    pdf_path = db.Column(db.String(200))

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100))
    score = db.Column(db.Integer)
    course = db.Column(db.String(100))

# Forms
class RegisterForm(FlaskForm):
    mobile = StringField('Mobile', validators=[DataRequired(), Length(10,10)])
    submit = SubmitField('Send OTP')

class VerifyOTPForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired(), Length(4,4)])
    submit = SubmitField('Verify')

class LoginForm(FlaskForm):
    mobile = StringField('Mobile', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class PaymentForm(FlaskForm):
    method = SelectField('Payment Method', choices=[('upi', 'UPI'), ('card', 'Credit/Debit Card'), ('netbank', 'Net Banking')])
    submit = SubmitField('Pay Now')

class AdminUploadForm(FlaskForm):
    course_id = IntegerField('Course ID')
    chapter = StringField('Chapter')
    video = FileField('Video')
    pdf = FileField('PDF')
    submit = SubmitField('Upload')

# Helpers
def login_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login required!')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

def admin_required(f):
    def wrap(*args, **kwargs):
        if 'user_id' not in session or not User.query.get(session['user_id']).is_admin:
            abort(403)
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

@app.route('/')
def index():
    courses = Course.query.limit(4).all()
    results = Result.query.all()
    return render_template('index.html', courses=courses, results=results)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        mobile = form.mobile.data
        if User.query.filter_by(mobile=mobile).first():
            flash('Mobile already registered!')
            return render_template('register.html', form=form)
        otp = str(random.randint(1000, 9999))
        session['pending_mobile'] = mobile
        session['otp'] = otp
        flash(f'OTP {otp} sent to {mobile} (simulated)')
        return redirect(url_for('verify_otp'))
    return render_template('register.html', form=form)

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    form = VerifyOTPForm()
    if form.validate_on_submit():
        if form.otp.data == session.get('otp'):
            mobile = session['pending_mobile']
user = User(mobile=mobile, password_hash=generate_password_hash('password123'), verified=True)
            db.session.add(user)
            db.session.commit()
            flash('Registered! Set password on login.')
            return redirect(url_for('login'))
        flash('Invalid OTP')
    return render_template('verify_otp.html', form=form)  # Note: add template later

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(mobile=form.mobile.data).first()
        if user and user.verified and check_password_hash(user.password_hash, form.password.data):
            session['user_id'] = user.id
            flash('Logged in!')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/courses')
@login_required
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll(course_id):
    enrollment = Enrollment(user_id=session['user_id'], course_id=course_id)
    db.session.add(enrollment)
    db.session.commit()
    return redirect(url_for('payment', enroll_id=enrollment.id))

@app.route('/payment/<int:enroll_id>', methods=['GET', 'POST'])
@login_required
def payment(enroll_id):
    form = PaymentForm()
    if form.validate_on_submit():
        # Simulate payment
        enrollment = Enrollment.query.get(enroll_id)
        enrollment.status = 'paid'
        db.session.commit()
        flash('Payment successful!')
        return redirect(url_for('dashboard'))
    enrollment = Enrollment.query.get(enroll_id)
    course = Course.query.get(enrollment.course_id)
    return render_template('payment.html', form=form, course=course)

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    enrollments = Enrollment.query.filter_by(user_id=user_id, status='paid').all()
    return render_template('dashboard.html', enrollments=enrollments)

@app.route('/video/<int:material_id>')
@login_required
def video(material_id):
    material = Material.query.get(material_id)
    return render_template('video.html', material=material)

@app.route('/admin')
@admin_required
def admin():
    enrollments = Enrollment.query.all()
    return render_template('admin.html', enrollments=enrollments)

@app.route('/admin/upload', methods=['POST'])
@admin_required
def admin_upload():
    form = AdminUploadForm()
    if form.validate_on_submit():
        course_id = request.form['course_id']
        chapter = request.form['chapter']
        video_file = request.files.get('video')
        pdf_file = request.files.get('pdf')
        if video_file and video_file.filename:
            filename = secure_filename(video_file.filename)
            video_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            material = Material(course_id=course_id, chapter=chapter, video_path=f'/static/videos/{filename}')
            db.session.add(material)
            db.session.commit()
            flash('Video uploaded!')
        if pdf_file and pdf_file.filename:
            filename = secure_filename(pdf_file.filename)
            pdf_file.save(os.path.join(app.config['PDF_FOLDER'], filename))
            # Update material pdf_path if new
            flash('PDF uploaded!')
    return redirect(url_for('admin'))

@app.route('/seed')
def seed():
    if Course.query.first() is None:
        courses = [
            Course(name='JEE Preparation', desc='Full JEE prep', duration='2 years', price=50000),
            Course(name='NEET Preparation', desc='Full NEET prep', duration='1 year', price=45000),
            Course(name='Engineering Entrance', desc='Eng entrance', duration='6 months', price=25000),
            Course(name='BCA Preparation', desc='BCA prep', duration='3 months', price=15000)
        ]
        for c in courses:
            db.session.add(c)
        db.session.add(Material(course_id=1, chapter='Chapter 1', video_path='/static/videos/sample.mp4', pdf_path='/static/pdfs/sample.pdf'))
        db.session.add(Result(student_name='John', score=98, course='JEE'))
        db.session.add(User(mobile='9999999999', password_hash=generate_password_hash('password123'), verified=True, is_admin=True))
        db.session.commit()
        flash('DB seeded!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
app.run(debug=True, host='0.0.0.0', port=5000)
