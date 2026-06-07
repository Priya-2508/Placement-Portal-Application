from flask import render_template, request , redirect, session ,url_for , flash
from applications import models
from applications.database import db
from datetime import datetime
from sqlalchemy import or_

def company_routes(app):
    
    @app.route('/company/companyDashboard',methods=['GET','POST','PUT'])
    def companyDashboard():
        print("HIT THIS ROUTE")
        print("METHOD:", request.method)
        user_id=session.get('user_id')
        company=models.Companies.query.filter_by(user_id=user_id).first()
        if request.method == 'POST':
            company.website = request.form.get('website')
            company.hr_contact = request.form.get('hr_contact')

            db.session.commit()
            flash("Profile updated successfully", "success")
            return redirect(url_for('companyDashboard'))
        
        drives=models.Drives.query.filter_by(company_id=company.company_id).all()
        return render_template('companyDashboard.html',drives=drives,company=company)
    
    

    @app.route('/admin/pendingApprovals',methods=['GET','POST'])
    def companyPendingApprovals():
        pending_companies = db.session.query(models.Companies).join(models.Users).filter(
        models.Companies.registration_status == 'pending'
    ).all()

        return render_template('pendingCompanyApprovals.html',companies=pending_companies)


    @app.route('/admin/pending-drives')
    def pending_drives():

        drives = db.session.query(models.Drives).join(models.Companies).join(models.Users).filter(
            models.Drives.status == 'pending'
        ).all()

        return render_template(
            'pendingDriveApprovals.html',
            drives=drives
        )

    @app.route('/company/approve/<int:id>')
    def approve_company(id):
        company=models.Companies.query.get(id)
        company.registration_status='approved'
        db.session.commit()
        return redirect(url_for('companyPendingApprovals'))
    
    
    
    @app.route('/company/reject/<int:id>')
    def reject_company(id):
        company=models.Companies.query.get(id)
        company.registration_status='rejected'
        db.session.commit()
        return redirect(url_for('companyPendingApprovals'))
    

    @app.route('/admin/approve-drive/<int:id>')
    def approve_drive(id):
        drive = models.Drives.query.get(id)
        drive.status = 'approved'
        db.session.commit()
        return redirect(url_for('pending_drives'))


    @app.route('/admin/reject-drive/<int:id>')
    def reject_drive(id):
        drive = models.Drives.query.get(id)
        drive.status = 'rejected'
        db.session.commit()
        return redirect(url_for('pending_drives'))
    
    @app.route('/company/createDrives',methods=['GET','POST'])
    def createDrive():
        if request.method=='POST':
            jobTitle=request.form['jobTitle']
            jobDescription=request.form['jobDescription']
            eligibilityCriteria=request.form['eligibility']
            cgpa=request.form['cgpa']
            driveDate=request.form['driveDate']
            deadline=request.form['deadline']
            user_id=session['user_id']
            company=models.Companies.query.filter_by(user_id=user_id).first()
            new_drive=models.Drives(company_id=company.company_id,job_title=jobTitle,job_description=jobDescription,eligibility_criteria=eligibilityCriteria,minimum_cgpa=cgpa,drive_date=driveDate,application_deadline=deadline)
            db.session.add(new_drive)
            db.session.commit()
            return redirect(url_for('companyDashboard'))
        return render_template('driveApplication.html')
    

    @app.route('/company/delete_drive/<int:id>')
    def delete_drive(id):
        drive=models.Drives.query.get(id)
        db.session.delete(drive)
        db.session.commit()
        return redirect(url_for('companyDashboard'))

    @app.route('/company/edit_drive/<int:id>', methods=['GET', 'POST'])
    def edit_drive(id):

        drive = models.Drives.query.get(id)

        if request.method == 'POST':
            drive.job_title = request.form.get('jobTitle')
            drive.job_description = request.form.get('jobDescription')
            drive.eligibility_criteria = request.form.get('eligibility')
            drive.minimum_cgpa = request.form.get('cgpa')
            drive.drive_date = request.form.get('driveDate')
            drive.application_deadline = request.form.get('deadline')

            db.session.commit()

            return redirect(url_for('companyDashboard'))

        return render_template('editDrive.html', drive=drive)
    
    @app.route('/company/ongoingCompanies')
    def ongoingCompanies():
        companies=db.session.query(models.Companies).join(models.Users).filter(
            models.Companies.registration_status=='approved').all()
        return render_template('ongoingCompanies.html',companies=companies)
    
    
    @app.route('/admin/delete_company/<int:id>')
    def delete_company(id):

        company = models.Companies.query.get(id)
        if company.drives: 
            flash("Cannot delete company with active drives", "danger")
            return redirect(url_for('ongoingCompanies'))
        db.session.delete(company)
        db.session.commit()

        return redirect(url_for('ongoingCompanies'))
    
    
    @app.route('/admin/company/<int:id>/drives')
    def company_drives(id):

        company = models.Companies.query.get(id)
        drives = models.Drives.query.filter_by(company_id=id).all()

        return render_template(
            'companyDrives.html',
            drives=drives,
            company=company
        )
    
    @app.route('/admin/ongoingDrives')
    def ongoing_drives():
        drives=db.session.query(models.Drives).join(models.Companies).join(models.Users).filter(models.Drives.status=='approved').all()
        today=datetime.today().date()

        ongoing_drives = []

        for d in drives:
            try:
                deadline = datetime.strptime(d.application_deadline, "%Y-%m-%d").date()
                drive_date = datetime.strptime(d.drive_date, "%Y-%m-%d").date()

                if drive_date >= today:
                    ongoing_drives.append(d)

            except:
                pass 

        return render_template('ongoingDrives.html',drives=ongoing_drives)
    

    @app.route('/admin/delete_drive/<int:id>')
    def delete_drive_admin(id):

        drive = models.Drives.query.get(id)
        if drive.applications: 
            flash("Cannot delete drive with student applications", "danger")
            return redirect(url_for('admin_drives'))
        db.session.delete(drive)
        db.session.commit()

        return redirect(url_for('admin_drives'))
    

    @app.route('/company/applications/<int:drive_id>')
    def view_applications(drive_id):

        applications = db.session.query(models.Applications)\
            .join(models.Students)\
            .join(models.Users)\
            .filter(models.Applications.drive_id == drive_id)\
            .all()

        drive = models.Drives.query.get(drive_id)

        return render_template(
            'viewApplications.html',
            applications=applications,
            drive=drive
        )
    

    @app.route('/company/application/update/<int:id>/<status>')
    def update_application(id, status):

        app_obj = models.Applications.query.get(id)

        if status in ['selected', 'rejected']:
            app_obj.status = status
            db.session.commit()

        return redirect(request.referrer)
    

    @app.route('/admin/block_company/<int:id>')
    def block_company(id):

        company = models.Companies.query.get(id)
        company.blocklist = 1
        db.session.commit()

        return redirect(url_for('ongoingCompanies'))
    
    @app.route('/admin/unblock_company/<int:id>')
    def unblock_company(id):
        company=models.Companies.query.get(id)
        company.blocklist=0
        db.session.commit()
        return redirect(url_for('ongoingCompanies'))
    

    @app.route('/admin/applications')
    def admin_applications():

        applications = db.session.query(models.Applications)\
            .join(models.Students)\
            .join(models.Users)\
            .join(models.Drives)\
            .join(models.Companies)\
            .all()

        return render_template('adminApplications.html', applications=applications)

    

    @app.route('/admin/drivesHistory')
    def admin_drives_history():

        companies = db.session.query(models.Companies)\
            .join(models.Users)\
            .all()

        drives = db.session.query(models.Drives)\
            .join(models.Companies)\
            .join(models.Users)\
            .all()

 
        applications = db.session.query(models.Applications)\
            .join(models.Students)\
            .join(models.Users)\
            .join(models.Drives)\
            .join(models.Companies)\
            .all()

        today = datetime.today().date()

        ongoing = []
        completed = []

        for d in drives:
            try:
                deadline = datetime.strptime(d.application_deadline, "%Y-%m-%d").date()

                if deadline >= today:
                    ongoing.append(d)
                else:
                    completed.append(d)
            except:
                completed.append(d)

        return render_template(
            'adminDrivesHistroy.html',
            companies=companies,
            ongoing_drives=ongoing,
            completed_drives=completed,
            applications=applications
        )
    
    @app.route('/admin/drive/<int:drive_id>/applications')
    def admin_drive_applications(drive_id):

        drive = models.Drives.query.get(drive_id)

        applications = db.session.query(models.Applications)\
            .join(models.Students)\
            .join(models.Users)\
            .filter(models.Applications.drive_id == drive_id)\
            .all()

        return render_template(
            'adminDriveApplications.html',
            applications=applications,
            drive=drive
        )
    
  

    @app.route('/admin/search', methods=['GET'])
    def admin_search():

        query = request.args.get('query')

        students = []
        companies = []

        if query:
            students = db.session.query(models.Students)\
                .join(models.Users)\
                .filter(
                    or_(
                        models.Users.username.ilike(f"%{query}%"),
                        models.Students.student_id == query if query.isdigit() else False
                    )
                ).all()

            companies = db.session.query(models.Companies)\
                .join(models.Users)\
                .filter(
                    or_(
                        models.Users.username.ilike(f"%{query}%"),
                        models.Companies.company_id == query if query.isdigit() else False
                    )
                ).all()

        return render_template(
            'adminSearch.html',
            students=students,
            companies=companies,
            query=query
        )
    

    @app.route('/admin/drive/<int:drive_id>/selected')
    def selected_students(drive_id):

        drive = models.Drives.query.get(drive_id)

        selected_apps = db.session.query(models.Applications)\
            .join(models.Students)\
            .join(models.Users)\
            .filter(
                models.Applications.drive_id == drive_id,
                models.Applications.status == 'selected'
            ).all()

        return render_template(
            'selectedStudents.html',
            applications=selected_apps,
            drive=drive
        )