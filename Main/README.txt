PLACEMENT PORTAL APPLICATION
----------------------------

Frameworks Used:
- Flask (Backend)
- Flask-SQLAlchemy
- Flask-Login
- SQLite (Database)
- Bootstrap (Frontend)

How to Run:
1. Install dependencies:
   pip install -r requirements.txt

2. Run the application:
   python app.py

3. Open browser:
   http://127.0.0.1:5000

Default Admin Credentials:
Email: admin@portal.com
Password: admin123

Features:
- Role-based authentication (Admin, Student, Company)
- Company approval by admin
- Placement drive creation
- Student applications
- Duplicate application prevention
- Dashboard statistics
- SQLite DB created programmatically

Database:
The SQLite database is created automatically when the app runs.
No manual DB creation is required.

Important Notes:
- No JavaScript used for core functionality.
- Admin is pre-created automatically.
- Unique constraint prevents multiple applications.

End of README