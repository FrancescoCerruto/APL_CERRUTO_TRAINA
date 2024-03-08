import requests
from functools import wraps
from project import create_app
from flask import render_template, redirect, request, flash, session, g
from redis import Redis
import os
import json

app = create_app()


def get_redis():
    if 'redis' not in g:
        g.redis = Redis(host=os.getenv("REDIS_HOST"), port=int(os.getenv("REDIS_PORT")), socket_timeout=5)
    # In Flask, the g object is a global variable that is available throughout
    # the lifetime of a request. It's primarily used to store data that needs to be
    # accessible across different parts of the request handling process,
    # such as different functions or middleware.
    return g.redis


# decorator - check if there is a logged user
def check_user_logged(f):
    @wraps(f)
    def user_logged(*args, **kwargs):
        # retrieve eventually user data
        if session.get('student_data'):
            # user data found --> user logged
            return f(session.get('student_data')['student_code'], session.get('student_data')['professor_code'], session.get('student_data')['subject'], *args, **kwargs)
        else:
            # user data not found --> redirect to login
            flash("Please login")
            return redirect('/login')
    return user_logged


@app.route('/')
def home():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        student_code = request.form['student_code']
        professor_code = request.form['professor_code']
        subject = request.form['subject']

        if "" in [student_code, subject, professor_code]:
            flash("Empty form")
            return redirect('/login')

        # call authenticationserver
        data_post = {
            'StudentCode': student_code,
            'ProfessorCode': professor_code,
            'Subject': subject
        }
        response = requests.post("http://authenticationserver:80/api/User/authenticate_student", data=data_post)

        if response.status_code == 200:
            # set cookie
            user_session = {'student_code': student_code, 'professor_code': professor_code, 'subject': subject, 'ended': False}
            session['student_data'] = user_session
            return redirect('/start_exam')
        if response.status_code == 404:
            flash("Student not allowed to execute exam")
            return redirect('/login')
        flash(response.content.decode())
        return redirect('/login')

    # get request
    # user already logged
    if session.get('student_data'):
        return redirect('/start_exam')

    # login required
    return render_template('login.html')


@app.route('/start_exam', methods=['GET', 'POST'])
@check_user_logged
def start_exam(student_code, professor_code, subject):
    if request.method == 'POST':
        # i have already created exam --> start execution
        return redirect('/execute')

    # get request

    # check if student has a local exam stored --> execute
    if get_redis().get(student_code) is None:
        # not stored locally --> deleted or not created?

        # check if student already submitted an exam
        # call studentcontroller
        data_post = {
            'StudentCode': student_code,
            'ProfessorCode': professor_code,
            'Subject': subject
        }
        response = requests.post("http://studentcontroller:80/api/Student/check_exam", data=data_post)

        # student already created an exam
        if response.status_code == 400:
            # student already created and submitted an exam
            # update cookie
            user_session = {'student_code': student_code, 'professor_code': professor_code, 'subject': subject,
                            'ended': True}
            session['student_data'] = user_session
            return redirect('/end')

        # prof not upload questions or parameters (response from exam manager 500 or 404)
        if response.status_code != 200:
            flash(response.content.decode())
            return render_template('start_exam.html')

        # exam created --> store in redis
        questions = []
        for question in json.loads(response.content.decode())['questions']:
            questions.append(question)
        data = {
            'questions': questions,
            'number_question': 0,
            'answers': []
        }
        get_redis().set(student_code, json.dumps(data))

        return render_template('start_exam.html')

    # student has an exam
    return redirect('/execute')


@app.route('/execute', methods=['GET', 'POST'])
@check_user_logged
def execute_exam(student_code, professor_code, subject):
    if get_redis().get(student_code) is None:
        return redirect('/start_exam')

    # retrieve exam data from redis
    exam_data = json.loads(get_redis().get(student_code))
    questions_list = exam_data['questions']
    number_execute = exam_data['number_question']
    question = questions_list[number_execute]

    if request.method == 'POST':
        # retrieve response
        new_answers = request.form.getlist('check')

        # store response (append to old answers)
        data_new = {
            'id_question': question['id_question'],
            'answers': new_answers
        }
        old_answers = exam_data['answers']
        old_answers.append(data_new)
        data = {
            'questions': questions_list,
            'number_question': number_execute + 1,
            'answers': old_answers
        }
        get_redis().set(student_code, json.dumps(data))

        # Check if the number of executions doesn't exceed the number of questions
        if len(questions_list) == number_execute + 1:
            # send answers to exam manager
            exam_data = json.loads(get_redis().get(student_code))
            answers = exam_data['answers']

            # call student controller
            data_post = {
                'StudentCode': student_code,
                'ProfessorCode': professor_code,
                'Subject': subject,
                'Answers': json.dumps(answers)
            }
            response = requests.post("http://studentcontroller:80/api/Student/end_exam", data=data_post)

            for row in response.content.decode()[1:-1].split(","):
                flash(row)

            # delete local exam
            get_redis().delete(student_code)
            # update cookie
            user_session = {'student_code': student_code, 'professor_code': professor_code, 'subject': subject, 'ended': True}
            session['student_data'] = user_session
            return redirect('/end')

        return redirect('/execute')

    # render new question
    return render_template('execute_exam.html', question=question['text'], answers=question['answers'])


@app.route('/end')
@check_user_logged
def end_exam(student_code, professor_code, subject):
    if not session.get('student_data')['ended']:
        return redirect('/start_exam')

    # call student controller - retrieve result
    data_post = {
        'StudentCode': student_code,
        'ProfessorCode': professor_code,
        'Subject': subject,
    }
    response = requests.post("http://studentcontroller:80/api/Student/retrieve_result", data=data_post)

    return render_template('end_exam.html', result=response.content.decode())


@app.route('/logout')
@check_user_logged
def logout(student_code, professor_code, subject):
    session.pop('student_data')
    return redirect('/login')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)