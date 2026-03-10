from flask import Flask, render_template, redirect, url_for, request, flash
from config import Config
from models import db, User, Student, Company, PlacementDrive, Application
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = "static/uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
with app.app_context():
    db.create_all()

    if not User.query.filter_by(role="admin").first():
        admin = User(
            name="Admin",
            email="admin@portal.com",
            password=generate_password_hash("admin123"),
            role="admin",
            is_approved=True,
        )

        db.session.add(admin)
        db.session.commit()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/company/update_application/<int:id>/<status>")
@login_required
def update_application(id, status):

    application = Application.query.get_or_404(id)

    application.status = status

    db.session.commit()

    flash("Application status updated")

    return redirect(request.referrer)

@app.route("/admin/search_companies")
@login_required
def search_companies():

    query = request.args.get("q")

    companies = []

    if query:
        companies = Company.query.filter(
            Company.company_name.contains(query)
        ).all()

    return render_template(
        "admin_companies.html",
        companies=companies
    )

@app.route("/admin/search_students")
@login_required
def search_students():

    query = request.args.get("q")

    students = []

    if query:
        students = Student.query.filter(
            Student.roll_number.contains(query)
        ).all()

    return render_template(
        "admin_students.html",
        students=students
    )
# ---------------- CREATE DATABASE ----------------

with app.app_context():
    db.create_all()

    # Create admin if not exists
    if not User.query.filter_by(role="admin").first():
        admin = User(
            name="Admin",
            email="admin@portal.com",
            password=generate_password_hash("admin123"),
            role="admin",
            is_approved=True
        )
        db.session.add(admin)
        db.session.commit()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return redirect(url_for("login"))


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            if not user.is_approved:
                flash("Account awaiting admin approval.")
                return redirect(url_for("login"))

            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid login")

    return render_template("login.html")


# ---------------- LOGOUT ----------------

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------------- REGISTER STUDENT ----------------

@app.route("/register/student", methods=["GET", "POST"])
def register_student():

    if request.method == "POST":

        user = User(
            name=request.form["name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"]),
            role="student",
            is_approved=True
        )

        db.session.add(user)
        db.session.commit()

        student = Student(
            user_id=user.id,
            roll_number=request.form["roll"],
            course=request.form["course"],
            cgpa=float(request.form["cgpa"])
        )

        db.session.add(student)
        db.session.commit()

        flash("Student registered successfully")
        return redirect(url_for("login"))

    return render_template("register_student.html")


# ---------------- REGISTER COMPANY ----------------

@app.route("/register/company", methods=["GET", "POST"])
def register_company():

    if request.method == "POST":

        user = User(
            name=request.form["company_name"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"]),
            role="company",
            is_approved=False
        )

        db.session.add(user)
        db.session.commit()

        company = Company(
            user_id=user.id,
            company_name=request.form["company_name"],
            hr_contact=request.form["hr"],
            website=request.form["website"],
            approval_status="Pending"
        )

        db.session.add(company)
        db.session.commit()

        flash("Company registered. Waiting for admin approval.")
        return redirect(url_for("login"))

    return render_template("register_company.html")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
@login_required
def dashboard():

    if current_user.role == "admin":

        students = Student.query.count()
        companies = Company.query.count()
        drives = PlacementDrive.query.count()
        applications = Application.query.count()

        return render_template(
            "admin_dashboard.html",
            students=students,
            companies=companies,
            drives=drives,
            applications=applications
        )

    elif current_user.role == "student":

        student = Student.query.filter_by(user_id=current_user.id).first()

        drives = PlacementDrive.query.filter_by(status="Approved").all()

        apps = Application.query.filter_by(student_id=student.id).all()

        return render_template(
            "student_dashboard.html",
            drives=drives,
            apps=apps
        )

    elif current_user.role == "company":

        company = Company.query.filter_by(user_id=current_user.id).first()

        drives = PlacementDrive.query.filter_by(company_id=company.id).all()

        return render_template(
            "company_dashboard.html",
            drives=drives
        )


# ---------------- ADMIN COMPANY MANAGEMENT ----------------

@app.route("/admin/companies")
@login_required
def manage_companies():

    companies = Company.query.all()

    return render_template(
        "manage_companies.html",
        companies=companies
    )


@app.route("/admin/approve_company/<int:id>")
@login_required
def approve_company(id):

    company = Company.query.get(id)
    company.approval_status = "Approved"

    user = User.query.get(company.user_id)
    user.is_approved = True

    db.session.commit()

    return redirect(url_for("manage_companies"))


@app.route("/admin/reject_company/<int:id>")
@login_required
def reject_company(id):

    company = Company.query.get(id)
    company.approval_status = "Rejected"

    db.session.commit()

    return redirect(url_for("manage_companies"))


# ---------------- ADMIN DRIVE MANAGEMENT ----------------

@app.route("/admin/drives")
@login_required
def manage_drives():

    drives = PlacementDrive.query.all()

    return render_template(
        "manage_drives.html",
        drives=drives
    )


@app.route("/admin/approve_drive/<int:id>")
@login_required
def approve_drive(id):

    drive = PlacementDrive.query.get(id)
    drive.status = "Approved"

    db.session.commit()

    return redirect(url_for("manage_drives"))


@app.route("/admin/reject_drive/<int:id>")
@login_required
def reject_drive(id):

    drive = PlacementDrive.query.get(id)
    drive.status = "Rejected"

    db.session.commit()

    return redirect(url_for("manage_drives"))


# ---------------- COMPANY CREATE DRIVE ----------------

@app.route("/company/create_drive", methods=["GET", "POST"])
@login_required
def create_drive():

    company = Company.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":

        drive = PlacementDrive(
            company_id=company.id,
            job_title=request.form["job_title"],
            job_description=request.form["description"],
            eligibility=request.form["eligibility"],
            deadline=datetime.strptime(request.form["deadline"], "%Y-%m-%d"),
            status="Pending"
        )

        db.session.add(drive)
        db.session.commit()

        flash("Drive created. Waiting admin approval")

        return redirect(url_for("dashboard"))

    return render_template("create_drive.html")

#---------------- ADMIN STUDENTS VIEW ---------------
@app.route("/admin/all_students")
@login_required
def all_students():

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    students = Student.query.all()

    return render_template("admin_students.html", students=students)

#------------------ ADMIN COMPANY VIEW-------------
@app.route("/admin/all_companies")
@login_required
def all_companies():

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    companies = Company.query.all()

    return render_template("admin_companies.html", companies=companies)

#----------------- ADMIN DRIVE VIEW-------------
@app.route("/admin/all_drives")
@login_required
def all_drives():

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))

    drives = PlacementDrive.query.all()

    return render_template("admin_drives.html", drives=drives)

#---------------- COMPANY APPLICATIONS-----------
@app.route("/company/view_applications/<int:drive_id>")
@login_required
def view_applications(drive_id):

    drive = PlacementDrive.query.get_or_404(drive_id)

    applications = Application.query.filter_by(drive_id=drive_id).all()

    student_details = []

    for app in applications:
        student = Student.query.get(app.student_id)
        user = User.query.get(student.user_id)

        student_details.append({
            "name": user.name,
            "roll": student.roll_number,
            "course": student.course,
            "cgpa": student.cgpa,
            "status": app.status
        })

    return render_template(
        "company_applications.html",
        students=student_details
    )

#-----------KICK COMPANY---------
@app.route("/admin/kick_company/<int:id>")
@login_required
def kick_company(id):

    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    company = Company.query.get_or_404(id)
    user = User.query.get(company.user_id)
    company.approval_status = "Kicked"

    Company.kicked = True
    User.is_active_user = False


    User.is_active_user = False

    db.session.commit()

    flash("Company has been kicked from the portal")

    return redirect(url_for("manage_companies"))

# ---------------- STUDENT APPLY ----------------

@app.route("/apply/<int:drive_id>")
@login_required
def apply(drive_id):

    student = Student.query.filter_by(user_id=current_user.id).first()

    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=drive_id
    ).first()

    if existing:
        flash("Already applied")
        return redirect(url_for("dashboard"))

    application = Application(
        student_id=student.id,
        drive_id=drive_id,
        status="Applied"
    )

    db.session.add(application)
    db.session.commit()

    flash("Application submitted")

    return redirect(url_for("dashboard"))


# ---------------- RUN APP ----------------

if __name__ == "__main__":

    app.run(debug=True)


