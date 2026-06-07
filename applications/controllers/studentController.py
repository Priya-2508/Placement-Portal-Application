from flask import render_template, request , redirect, session ,url_for , flash
from applications import models
from applications.database import db
from werkzeug.utils import secure_filename
import os
from datetime import datetime

def student_routes(app):

    from datetime import datetime

    @app.route('/student/dashboard')
    def student_dashboard():

        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))

        student = models.Students.query.filter_by(user_id=user_id).first()

        if not student:
            return "Student not found"

        drives = models.Drives.query.filter_by(status='approved').all()

        applications = models.Applications.query.filter_by(
            student_id=student.student_id
        ).all()


        today = datetime.today().strftime('%Y-%m-%d')

        return render_template(
            'studentDashboard.html',
            drives=drives,
            student=student,
            applications=applications,
            today=today
        )


    @app.route('/admin/students')
    def admin_students():

        students = db.session.query(models.Students)\
            .join(models.Users)\
            .all()

        return render_template('adminStudents.html', students=students)
    

    @app.route('/admin/block_student/<int:id>')
    def block_student(id):

        student = models.Students.query.get(id)
        student.blocklist = 1
        db.session.commit()

        return redirect(url_for('admin_students'))
    
    

    @app.route('/admin/unblock_student/<int:id>')
    def unblock_student(id):

        student = models.Students.query.get(id)
        student.blocklist = 0
        db.session.commit()

        return redirect(url_for('admin_students'))
    

    @app.route('/admin/delete_student/<int:id>')
    def delete_student(id):

        student = models.Students.query.get(id)
        db.session.delete(student)
        db.session.commit()

        return redirect(url_for('admin_students'))
    

    @app.route('/apply/<int:drive_id>')
    def apply_drive(drive_id):

        if 'user_id' not in session:
            return redirect(url_for('login'))

        student = models.Students.query.filter_by(user_id=session['user_id']).first()
        drive = models.Drives.query.get(drive_id)

        today = datetime.today().date()
        deadline = datetime.strptime(drive.application_deadline, "%Y-%m-%d").date()

        if today > deadline:
            flash("Cannot apply. Deadline is over!", "danger")
            return redirect(url_for('student_dashboard'))

        # prevent duplicate apply
        existing = models.Applications.query.filter_by(
            student_id=student.student_id,
            drive_id=drive_id
        ).first()

        if existing:
            flash("Already applied!", "warning")
            return redirect(url_for('student_dashboard'))

        application = models.Applications(
            student_id=student.student_id,
            drive_id=drive_id
        )

        db.session.add(application)
        db.session.commit()

        flash(" Applied successfully!", "success")
        return redirect(url_for('student_dashboard'))

    


    @app.route('/student/profile', methods=['GET', 'POST'])
    def student_profile():

        user_id=session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))
        
        student = models.Students.query.filter_by(user_id=session['user_id']).first()

        if request.method == 'POST':

            student.department = request.form.get('department')
            student.cgpa = request.form.get('cgpa')

            file = request.files.get('resume')

            if file and file.filename != "":
                filename = secure_filename(file.filename)

                upload_folder = os.path.join(app.root_path, 'static', 'resumes')
                os.makedirs(upload_folder, exist_ok=True)
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)

                student.resume = filename   # ✅ store only filename

            db.session.commit()
            return redirect(url_for('student_profile'))

        return render_template('studentProfile.html', student=student)