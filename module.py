from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(120))
    career_goal = db.Column(db.String(200))
    location = db.Column(db.String(120))
    school = db.Column(db.String(200))
    grade = db.Column(db.String(50))
    subjects = db.Column(db.String(200))
    interests = db.Column(db.Text)
    guidelines = db.Column(db.Text)
    profile_pic = db.Column(db.String(200))
