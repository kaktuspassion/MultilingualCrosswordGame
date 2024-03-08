import os
import traceback
from flask import request, jsonify, render_template, redirect, url_for, flash
from data_process import load_processed_data, select_word_clue_list
from crossword_generator import generate_crossword
from werkzeug.security import generate_password_hash, check_password_hash

from register import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 初始化 SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.secret_key = 'word_wizard_secret_key'
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///default.db').replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # 注册 SQLAlchemy 实例到 Flask 应用

    migrate = Migrate(app, db)  # 初始化 Flask-Migrate

    # 在这里注册你的蓝图或定义路由

    return app

# 从这里导入需要使用db对象的模块，例如模型定义，以避免循环依赖
from register import User

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)


# Load and process data for each language
english_data = load_processed_data('english')
spanish_data = load_processed_data('spanish')
french_data = load_processed_data('french')
dutch_data = load_processed_data('dutch')
swedish_data = load_processed_data('swedish')


@app.route('/')
def homepage():
    return render_template('homepage.html')


users_list = []


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        age = request.form.get('age')
        native_language = request.form.get('native_language')
        goals = request.form.getlist('goals')
        target_language = request.form.get('target_language')
        proficiency_level = request.form.get('proficiency_level')
        password = request.form.get('password')

        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'status': 'fail', 'message': 'Username already exists'}), 400

        # Create a new User instance
        goals_str = ', '.join(request.form.getlist('goals'))
        new_user = User(
            username=username,
            age=int(age),
            native_language=native_language,
            goals=goals_str,  # Assuming goals is already in the proper format for JSON storage
            target_language=target_language,
            proficiency_level=proficiency_level,
            password=password  # The password will be hashed in the User model's __init__ method
        )

        # Add the new User instance to the session
        db.session.add(new_user)

        try:
            # Commit the session to save the User to the database
            db.session.commit()
            flash('Signup successful. Please sign in.', 'success')  # Optional: Flash a success message
            return redirect(url_for('signin'))
        except Exception as e:
            # For production applications, log the exception here
            db.session.rollback()
            flash('An error occurred during registration.', 'error')  # Optional: Flash an error message
            print("Registration error:", traceback.format_exc())
            return render_template('signup.html')

    # Render the signup form template for GET requests
    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Assuming you are managing user sessions
            # session['user_id'] = user.id  # Log in the user

            # Redirect to the crossword page after successful sign in
            return redirect(url_for('crossword'))
        else:
            # If login is unsuccessful, flash a message and redirect back to sign in
            flash('Invalid username or password', 'danger')
            return redirect(url_for('signin'))

    # If it's a GET request, render the sign-in page
    return render_template('signin.html')


@app.route('/generate_crossword', methods=['GET'])
def generate_crossword_route():
    # request the data
    language = request.args.get('language', 'English')
    # request CEFR level
    cefr_level = request.args.get('level', 'a1')

    # according to the selected language to deal with the data
    language_data = {
        'English': english_data,
        'Spanish': spanish_data,
        'French': french_data,
        'Dutch': dutch_data,
        'Swedish': swedish_data
    }.get(language, english_data)

    # According to selected language and cefr level to generate the puzzle words randomly
    puzzle_words = select_word_clue_list(language_data, cefr_level, num_words=20)

    #
    puzzle = generate_crossword(puzzle_words)
    print(puzzle)

    return jsonify({"puzzle": puzzle})


@app.route('/crossword')
def crossword():
    return render_template('crossword.html')


if __name__ == '__main__':
    app.run(debug=True)
