from flask import Flask
from applications.config import Config 
from applications.database import db
from applications import models 
from applications.controllers.authController import auth_routes
from applications.controllers.companyController import company_routes
from applications.controllers.studentController import student_routes
import os
import sys


app=Flask(__name__)
app.config.from_object(Config)
app.secret_key="hello"
UPLOAD_FOLDER = 'static/resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
auth_routes(app)
company_routes(app)
student_routes(app)

db.init_app(app)
with app.app_context():
    db.create_all()

    admin=models.Users.query.filter_by(role='admin').first()

    if not admin:
        admin_user=models.Users(
            username='admin',
            email='admin@gmail.com',
            password='admin123',
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Admin created")

if __name__=="__main__":
    app.run(debug=True)
    print("running")

