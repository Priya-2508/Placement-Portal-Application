from flask import render_template, request , redirect, session ,url_for , flash
from applications import models
from applications.database import db

def auth_routes(app):

    @app.route('/')
    def home():
        return render_template('home.html')

    
    @app.route('/admin/adminDashboard')
    def adminDashboard():

        total_students = models.Students.query.count()
        total_companies = models.Companies.query.count()
        total_drives = models.Drives.query.count()
        total_applications = models.Applications.query.count()
        approved_companies = models.Companies.query.filter_by(registration_status='approved').count()
        pending_companies = models.Companies.query.filter_by(registration_status='pending').count()

        return render_template(
            'adminDashboard.html',
            total_students=total_students,
            total_companies=total_companies,
            total_drives=total_drives,
            total_applications=total_applications,
            approved_companies=approved_companies,
            pending_companies=pending_companies
        )
    

    @app.route('/login',methods=['POST','GET'])
    def login():
        if request.method=='POST':
            email=request.form['email']
            password=request.form['password']

            user=models.Users.query.filter_by(email=email,password=password).first()

            if user:
                session['user_id']=user.user_id
                session['role']=user.role

                if user.role=='admin':

                    return redirect(url_for('adminDashboard'))

                elif user.role=='student':
                    student = models.Students.query.filter_by(user_id=user.user_id).first()
                    if student.blocklist == 1:
                        return "You are blocked by admin"
                    return redirect(url_for('student_dashboard'))

                elif user.role=='company':
                    company=models.Companies.query.filter_by(user_id=user.user_id).first()

                    if company.blocklist==1:
                        return "You are blocked by admin"

                    if company.registration_status=='pending':
                        flash("Your approval is pending. You cannot login.")
                        return redirect(url_for('login'))

                    elif company.registration_status=='rejected':
                        flash("Your request has been rejected.Try again")
                        return redirect(url_for('login'))

                    return redirect(url_for('companyDashboard'))

            flash("Invalid Credentials", "danger")
            return redirect(url_for('login'))

        return render_template('login.html')

    @app.route('/register/student',methods=['GET','POST'])
    def registerAsStudent():
        if request.method=="POST":
            name=request.form['username']
            email=request.form['email']
            department=request.form['department']
            password=request.form['password']

            user=models.Users.query.filter_by(email=email).first()

            if user:
                return('You already have an account. Please login')
            
            new_user=models.Users(username=name,email=email,password=password,role='student')
            db.session.add(new_user)
            db.session.commit()

            new_student=models.Students(user_id=new_user.user_id,department=department)
            db.session.add(new_student)
            db.session.commit()

            return redirect(url_for('student_dashboard'))
        
        return render_template('studentRegistration.html')

    
    @app.route('/register/company',methods=['GET','POST'])
    def registerAsCompany():
        if request.method=="POST":
            name=request.form['name']
            email=request.form['email']
            website=request.form['website']
            hr_contact=request.form['hr_contact']
            password=request.form['password']

            user=models.Users.query.filter_by(email=email).first()
            

            if user:
                company=models.Companies.query.filter_by(user_id=user.user_id).first()
                if company:
                    if company.registration_status == 'rejected':
                        flash(" Your request was rejected. Contact admin.", "danger")

                    elif company.registration_status == 'pending':
                        flash(" Your request was rejected. Contact admin.", "danger")
                    elif company.registration_status == 'approved':
                        flash(" Account already exists. Please login.", "success")
                    return redirect(url_for('registerAsCompany'))

                flash(" User exists but no company profile. Contact admin.", "danger")
                return redirect(url_for('registerAsCompany'))
                
            new_user=models.Users(username=name,email=email,password=password,role='company')
            db.session.add(new_user)
            db.session.commit()

            new_company=models.Companies(user_id=new_user.user_id,website=website,hr_contact=hr_contact)
            db.session.add(new_company)
            db.session.commit()
            flash("Waiting for admins approval. You can login once admin approved your request")
            return redirect(url_for('registerAsCompany'))
        
        return render_template('companyRegistration.html')
        

    @app.route('/logout')
    def logout():
        session.clear() 
        return redirect(url_for('login'))

