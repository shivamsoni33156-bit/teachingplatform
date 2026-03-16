# GRAVITY - Coaching Institute Website

A professional coaching institute website for IIT/NEET preparation built with Flask and SQLite.

## Features

### User Features
- **Homepage**: Banner with motivational tagline, featured courses, student success stories, testimonials
- **Course Listing**: Display courses (JEE, NEET, Engineering Entrance, BCA) with descriptions, duration, and pricing
- **Student Login/Registration**: OTP verification system and password-based login
- **Payment**: Secure payment gateway integration (UPI, Credit/Debit Card, Net Banking)
- **Student Dashboard**: Enrolled courses, video lectures, PDF study materials, progress tracking
- **Study Material**: Embedded video player, chapter-wise content, downloadable PDFs

### Admin Features
- Upload videos and PDF study materials
- Add/edit courses
- Manage student enrollments
- View student data and progress

## Technology Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python Flask
- **Database**: SQLite

## Project Structure

```
GRAVITY/
├── app.py                 # Flask application
├── database.db            # SQLite database (auto-created)
├── README.md             # This file
├── TODO.md               # Project TODO list
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   ├── videos/           # Video storage
│   └── pdfs/             # PDF storage
└── templates/
    ├── index.html        # Homepage
    ├── login.html        # Login/Registration
    ├── courses.html      # Course listing
    ├── payment.html     # Payment page
    ├── dashboard.html   # Student dashboard
    ├── study_material.html  # Video & materials
    └── admin.html       # Admin panel
```

## Installation & Setup

### Prerequisites
- Python 3.7+
- Flask

### Install Dependencies
```bash
pip install flask
```

### Run the Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

## Default Login Credentials

### Admin Account
- **Phone**: 9999999999
- **Password**: admin123

### Access Admin Panel
1. Login with admin credentials
2. Navigate to Dashboard
3. Click "Admin Panel" in navigation

## Demo Flow

1. **Browse Courses**: Visit homepage or courses page
2. **Register/Login**: Use OTP or password login
3. **Enroll**: Click "Enroll Now" on a course
4. **Payment**: Select payment method and complete payment
5. **Access Content**: View enrolled courses in dashboard
6. **Study**: Watch videos and download PDFs

## Pages Overview

- **Homepage** (`/`): Hero banner, featured courses, testimonials, footer
- **Courses** (`/courses`): All available courses with details
- **Login** (`/login`): OTP and password authentication
- **Dashboard** (`/dashboard`): Student enrolled courses and progress
- **Payment** (`/payment/<id>`): Payment gateway (simulated)
- **Study Material** (`/study_material/<id>`): Video player and PDF downloads
- **Admin** (`/admin`): Content management and student data

## Notes

- Payment is simulated (no real payment gateway integration)
- OTP is displayed in the response for demo purposes
- Default password for new users is their phone number
- Video and PDF uploads are handled through admin panel

