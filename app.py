from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hw13.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELS
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100))
    num_questions = db.Column(db.Integer)
    quiz_date = db.Column(db.Date)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'))
    score = db.Column(db.Integer)

# LOGIN CHECK
def login_required(f):
    def wrap(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect('/login')
        return f(*args, **kwargs)
    wrap.__name__ = f.__name__
    return wrap

# INIT DB + SAMPLE DATA
@app.before_first_request
def setup():
    db.create_all()

    if Student.query.count() == 0:
        student = Student(first_name="John", last_name="Smith")
        db.session.add(student)

        quiz = Quiz(
            subject="Python Basics",
            num_questions=5,
            quiz_date=datetime(2015, 2, 5)
        )
        db.session.add(quiz)
        db.session.commit()

        result = Result(student_id=student.id, quiz_id=quiz.id, score=85)
        db.session.add(result)
        db.session.commit()

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            return redirect('/dashboard')
        else:
            flash("Wrong credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# DASHBOARD
@app.route('/dashboard')
@login_required
def dashboard():
    students = Student.query.all()
    quizzes = Quiz.query.all()
    return render_template('dashboard.html', students=students, quizzes=quizzes)

# ADD STUDENT
@app.route('/student/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        s = Student(
            first_name=request.form['first_name'],
            last_name=request.form['last_name']
        )
        db.session.add(s)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('add_student.html')

# ADD QUIZ
@app.route('/quiz/add', methods=['GET', 'POST'])
@login_required
def add_quiz():
    if request.method == 'POST':
        q = Quiz(
            subject=request.form['subject'],
            num_questions=int(request.form['num_questions']),
            quiz_date=datetime.strptime(request.form['quiz_date'], '%Y-%m-%d')
        )
        db.session.add(q)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('add_quiz.html')

# ADD RESULT
@app.route('/results/add', methods=['GET', 'POST'])
@login_required
def add_result():
    students = Student.query.all()
    quizzes = Quiz.query.all()

    if request.method == 'POST':
        r = Result(
            student_id=int(request.form['student_id']),
            quiz_id=int(request.form['quiz_id']),
            score=int(request.form['score'])
        )
        db.session.add(r)
        db.session.commit()
        return redirect('/dashboard')

    return render_template('add_result.html', students=students, quizzes=quizzes)

# VIEW RESULTS
@app.route('/student/<int:id>')
@login_required
def student_results(id):
    results = Result.query.filter_by(student_id=id).all()
    return render_template('student_results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)