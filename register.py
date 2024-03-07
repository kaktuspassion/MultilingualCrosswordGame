from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Create an instance of SQLAlchemy
db = SQLAlchemy()

# Define the User model


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    native_language = db.Column(db.String(80), nullable=False)
    goals = db.Column(db.String, nullable=False)
    target_language = db.Column(db.String(80), nullable=False)
    proficiency_level = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def __init__(self, username, age, native_language, goals, target_language, proficiency_level, password):
        self.username = username
        self.age = age
        self.native_language = native_language
        self.goals = goals
        self.target_language = target_language
        self.proficiency_level = proficiency_level
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
