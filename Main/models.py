from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # admin, student, company
    is_approved = db.Column(db.Boolean, default=False)
    is_active_user = db.Column(db.Boolean, default=True)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    roll_number = db.Column(db.String(50))
    course = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    resume = db.Column(db.String(200))


class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(150))
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(150))
    approval_status = db.Column(db.String(20), default="Pending")
    kicked = db.Column(db.Boolean, default=False)

class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    job_title = db.Column(db.String(150))
    job_description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default="Pending")


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'))
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Applied")

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),
    )