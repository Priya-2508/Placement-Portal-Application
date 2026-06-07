from applications.database import db

class Users(db.Model):
    __tablename__='users'
    user_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(100))
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))
    role=db.Column(db.String(15))
    company = db.relationship('Companies', back_populates='user', uselist=False)

class Students(db.Model):
    __tablename__='students'
    student_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.user_id'))
    blocklist=db.Column(db.Integer,default=0)
    cgpa = db.Column(db.Float)
    resume = db.Column(db.String(200))
    department=db.Column(db.String(100))
    user = db.relationship('Users', backref='student', uselist=False)
    applications = db.relationship('Applications', back_populates='student',lazy=True)

class Companies(db.Model):
    __tablename__='companies'
    company_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    user_id=db.Column(db.Integer,db.ForeignKey('users.user_id'))
    website=db.Column(db.String(100),unique=True)
    hr_contact=db.Column(db.String(13))
    registration_status=db.Column(db.String(20),default='pending')
    blocklist = db.Column(db.Integer, default=0)
    user = db.relationship('Users', back_populates='company')
    drives = db.relationship(
        'Drives',
        backref='company',
    )

class Drives(db.Model):
    __tablename__ = 'drives'

    drive_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id')) 

    job_title = db.Column(db.String(100))
    job_description = db.Column(db.String(1000))
    eligibility_criteria = db.Column(db.String(1000))
    minimum_cgpa = db.Column(db.String(5))
    drive_date = db.Column(db.String(20))
    application_deadline = db.Column(db.String(20))

    status = db.Column(db.String(20), default='pending') 
    applications = db.relationship(
        'Applications',
        back_populates='drive',
    )



class Applications(db.Model):
    __tablename__ = 'applications'

    application_id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('drives.drive_id'))

    status = db.Column(db.String(20), default='applied')  # applied / shortlisted / rejected / selected
    applied_on = db.Column(db.DateTime, default=db.func.current_timestamp())

    student = db.relationship(
        'Students',
        back_populates='applications'
    )
    drive = db.relationship(
    'Drives',
    back_populates='applications'
)

