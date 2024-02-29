import requests
from functools import wraps
from project import create_app
from flask import render_template, redirect, request, flash, session, send_from_directory, after_this_request
from werkzeug.utils import secure_filename
import os
import matplotlib.pyplot as plt
import json

app = create_app()
app.config['UPLOAD_FOLDER'] = app.root_path + "/static/uploads/"
app.config['IMAGES_FOLDER'] = app.root_path + "/static/images/"


# decorator - check if there is a logged user
def check_user_logged(f):
    @wraps(f)
    def user_logged(*args, **kwargs):
        # retrieve eventually user data
        if session.get('prof_data'):
            # user data found --> user logged
            return f(session.get('prof_data')['code'], session.get('prof_data')['subject'], *args, **kwargs)
        else:
            # user data not found --> redirect to login
            flash("Please login")
            return redirect('/login')
    return user_logged


def import_file_student(file, code, subject):
    # sanitizes filename (prevent directory traversal attacks and other security vulnerabilities)
    file_name = secure_filename(file.filename)
    file_path = app.config['UPLOAD_FOLDER'] + file_name
    # store file locally
    file.save(file_path)

    with open(file_path) as f:
        # number of student already stored in db
        duplicate = 0
        # number of student written in file but
        # that math on prof code and subject
        match = 0
        # number of record malformed (file csv written in standard format)
        record_format = 0

        # iterate for each row
        students_list = f.read().splitlines()
        for student in students_list:
            # file csv --> comma separated fields
            # required student_code, prof_code, subject
            if len(student.split("; ")) != 3:
                record_format = record_format + 1
                # flash of recap
                if record_format == 1:
                    flash("At least one line has a wrong format")
                continue

            # json data to store student
            data_post = {
                'StudentCode': student.split("; ")[0],
                'ProfessorCode': student.split("; ")[1],
                'Subject': student.split("; ")[2]
            }

            # match student and prof
            if data_post['Subject'] != subject or data_post['ProfessorCode'] != code:
                match = match + 1
                # flash of recap
                if match == 1:
                    flash("At least one student in the list doesn't match with the professor subject")
                elif match == len(students_list):
                    flash("Error - upload file with your code and subject")

                    # delete file at the end of the request
                    @after_this_request
                    def removeFile(after_response):
                        os.remove(app.config['UPLOAD_FOLDER'] + file_name)
                        return after_response

                    return redirect('/add_student')
                continue

            # store student
            response = requests.post("http://authenticationserver:80/api/User/add_student", data=data_post)
            if response.status_code == 200:
                continue
            elif response.status_code == 400:
                # drop insert
                flash("Unable to add students")

                # delete file at the end of the request
                @after_this_request
                def removeFile(after_response):
                    os.remove(app.config['UPLOAD_FOLDER'] + file_name)
                    return after_response

                return redirect('/add_student')
            elif response.status_code == 500:
                duplicate = duplicate + 1

        # Just to notify what really happened with the file
        if duplicate == 0 and record_format < len(students_list):
            flash("Students added successfully")
        elif duplicate == len(students_list) - match:
            flash("Duplicate file")
        elif len(students_list) == record_format:
            flash("All questions has wrong format")
        else:
            flash("Not duplicated students added successfully")

        # delete file at the end of the request
        @after_this_request
        def removeFile(after_response):
            os.remove(app.config['UPLOAD_FOLDER'] + file_name)
            return after_response

        return redirect('/add_student')


def import_file_questions(file, code, subject):
    # sanitizes filename (prevent directory traversal attacks and other security vulnerabilities)
    file_name = secure_filename(file.filename)
    file_path = app.config['UPLOAD_FOLDER'] + file_name
    # store file locally
    file.save(file_path)

    with open(file_path) as f:
        # number of questions already stored in db
        duplicate = 0
        # number of questions written in file but
        # that not math on prof code and subject
        match = 0
        # number of record malformed (file csv written in standard format)
        record_format = 0
        # autoincrement question
        id = 1

        # iterate for each row
        questions_list = f.read().splitlines()
        for question in questions_list:
            # file csv --> comma separated fields
            # required prof_code, subject, text, four answers, list of correct answers
            if len(question.split("; ")) != 8:
                record_format = record_format + 1
                # flash of recap
                if record_format == 1:
                    flash("At least one line has a wrong format")
                continue

            # json data to store question
            data_post = {
                'id': id,
                'code': question.split("; ")[0],
                'subject': question.split("; ")[1],
                'question': question.split("; ")[2],
                'answer1': question.split("; ")[3],
                'answer2': question.split("; ")[4],
                'answer3': question.split("; ")[5],
                'answer4': question.split("; ")[6],
                'correct_answer': question.split("; ")[7]
            }

            # match question and prof
            if data_post['subject'] != subject or data_post['code'] != code:
                match = match + 1
                if match == 1:
                    flash("At least one question in the list doesn't match with the professor subject")
                elif match == len(questions_list):
                    flash("Error - upload file with your code and subject")

                    # delete file at the end of the request
                    @after_this_request
                    def removeFile(after_response):
                        os.remove(app.config['UPLOAD_FOLDER'] + file_name)
                        return after_response

                    return redirect('/add_questions')
                continue

            # store question
            response = requests.post("http://exammanager:5000/add_question", data=data_post)
            id = id + 1
            if response.status_code == 200:
                # stored
                continue
            elif response.status_code == 400:
                # duplicated
                duplicate = duplicate + 1
            else:
                # database not reachable
                flash(response.content.decode())

                # delete file at the end of the request
                @after_this_request
                def removeFile(after_response):
                    os.remove(app.config['UPLOAD_FOLDER'] + file_name)
                    return after_response

                return redirect('/add_questions')

        # Just to notify what really happened with the file
        if duplicate == 0 and record_format < len(questions_list):
            flash("Questions added successfully")
        elif duplicate == len(questions_list) - match:
            flash("Duplicate file")
        elif len(questions_list) == record_format:
            flash("All questions has wrong format")
        else:
            flash("Not duplicated questions added successfully")

        # delete file at the end of the request
        @after_this_request
        def removeFile(after_response):
            os.remove(app.config['UPLOAD_FOLDER'] + file_name)
            return after_response

        return redirect('/add_questions')


@app.route('/')
def blank():
    return redirect('/login')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # object request.form is a dictionary --> indexing by name
        code = request.form['code']
        password = request.form['password']
        subject = request.form['subject']

        if "" in [code, password, subject]:
            flash("Empty form")
            return redirect('/register')

        # call auth_server
        data_post = {
            'code': code,
            'password': password,
            'subject': subject
        }
        response = requests.post("http://authenticationserver:80/api/User/add_professor", data=data_post)
        
        if response.status_code == 200:
            flash("Registration successfully completed")
            return redirect('/login')
        else:
            flash(response.content.decode())
            return redirect('/register')
    # get request
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # object request.form is a dictionary --> indexing by name
        code = request.form['code']
        password = request.form['password']
        subject = request.form['subject']

        if code == "" or password == "" or subject == "":
            flash("Empty form")
            return redirect('/login')

        # call auth_server
        data_post = {
            'code': code,
            'password': password,
            'subject': subject
        }
        response = requests.post("http://authenticationserver:80/api/User/authenticate_professor", data=data_post)

        if response.status_code == 200:
            # login --> save cookie
            user_session = {'code': code, 'subject': subject}
            session['prof_data'] = user_session
            return redirect('/home')
        elif response.status_code == 404:
            flash("Professor not registered")
            return redirect('/login')
        else:
            flash(response.content.decode())
            return redirect('/login')
    # get request
    # user already logged
    if session.get('prof_data'):
        return redirect('/home')
    # login required
    return render_template('login.html')


@app.route('/home')
@check_user_logged
def home(code, subject):
    return render_template('home.html', professor=code, subject=subject)


@app.route('/download', methods=['GET'])
@check_user_logged
def download(code, subject):
    # call filesharing --> obtain list files exams
    response = requests.get('http://filesharing:8080/files/{}/{}'.format(code, subject))

    # from response body to list of string printed on html page
    # remove first and last string (tag html)
    exams_list_tmp = response.content.decode().split("\n")[1:len(response.content.decode().split("\n"))-2]

    exams_list = []
    for exam in exams_list_tmp:
        # remove <a href="
        # obtain _.csv">_.csv</a>
        # get file name splitting on "
        exams_list.append(exam[9:].split("\"")[0])
    return render_template('download.html', exams=exams_list)


@app.route('/metrics')
@check_user_logged
def metrics(code, subject):
    # call professorcontroller
    data_post = {
        'ProfessorCode': code,
        'Subject': subject,
    }
    response = requests.post("http://professorcontroller:80/api/Prof/metrics", data=data_post)

    response_json = json.loads(response.content.decode())

    #In order in the json we have:
    # 0 created exams,
    # 1 finished exams,
    # 2 passed exams,
    # 3 passed exams percentage,
    # 4 failed exams percentage,
    # 5 exams time
    # 6 results
    # Creating plots based on these metrics

    # First bar plot --> created --> (finished, not finished) exams
    x = ['Created Exams', 'Finished Exams', 'Not Finished Exams']
    y = [float(response_json[0]), float(response_json[1]), float(response_json[0]) - float(response_json[1])]
    c = ['orange', 'green', 'red']
    plt.title("Completed Exams Overview")
    plt.bar(x, y, color=c)
    plt.savefig(app.config['IMAGES_FOLDER'] + 'first_plot.png')
    plt.clf()

    # Second bar plot --> finished --> (passed, failed) exams
    x = ['Finished Exams', 'Passed Exams', 'Failed Exams']
    y = [float(response_json[1]), float(response_json[2]), float(response_json[1]) - float(response_json[2])]
    c = ['orange', 'green', 'red']
    plt.title("Failed Exams Overview")
    plt.bar(x, y, color=c)
    plt.savefig(app.config['IMAGES_FOLDER'] + 'second_plot.png')
    plt.clf()

    # Third pie plot --> finished (passed_percentage, failed_percentage)
    names = 'Passed Exams\n Percentage ' + str(round(float(response_json[3]), 2)) + '%', 'Failed Exams\n Percentage ' + str(round(float(response_json[4]), 2)) + '%'
    values = [float(response_json[3]), float(response_json[4])]
    if values[0] > 0 or values[1] > 0:
        plt.pie(values, labels=names, labeldistance=1.15)
        plt.title("Exams Percentage")
        plt.savefig(app.config['IMAGES_FOLDER'] + 'third_plot.png')
        plt.clf()

    # Fourth scatter plot --> time metric
    time_response = json.loads(response_json[5][:-1])
    x = [x + 1 for x in range(0, len(time_response['single_time']), 1)]
    y1 = [float(value) for value in time_response['single_time']]
    y2 = [time_response['average_time'] for _ in range(len(time_response['single_time']))]
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x, y1, marker='D')
    ax1.plot(x, y2, marker='D')
    plt.legend(['delivery time', 'average delivery time'], loc='upper left')
    ax1.set_xlabel('Students')
    ax1.set_ylabel('Delivery time (s)')
    plt.title('Delivery time exams')
    plt.savefig(app.config['IMAGES_FOLDER'] + 'fourth_plot.png')
    plt.clf()

    # Fifth scatterplot --> result metric
    value_response = json.loads(response_json[6][:-1])
    x = [x + 1 for x in range(0, len(value_response['single_result']), 1)]
    y1 = [float(value) for value in value_response['single_result']]
    y2 = [value_response['average_result'] for _ in range(len(value_response['single_result']))]
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x, y1, marker='D')
    ax1.plot(x, y2, marker='D')
    plt.legend(['result', 'average result'], loc='upper left')
    ax1.set_xlabel('Students')
    ax1.set_ylabel('Result')
    plt.title('Results exams')
    plt.savefig(app.config['IMAGES_FOLDER'] + 'fifth_plot.png')
    plt.clf()

    return render_template('metrics.html', plot1='images/first_plot.png', plot2='images/second_plot.png', plot3='images/third_plot.png', plot4='images/fourth_plot.png', plot5='images/fifth_plot.png')


@app.route('/restore', methods=['GET', 'POST'])
@check_user_logged
def restore(code, subject):
    if request.method == 'POST':
        # call professorcontroller
        data_post = {
            'ProfessorCode': code,
            'Subject': subject
        }
        response = requests.post("http://professorcontroller:80/api/Prof/restore_system", data=data_post)

        if "," not in response.content.decode():
            flash(response.content.decode())
        else:
            # remove [], split on ',' and remove first and last char (")
            for row in response.content.decode()[1:-1].split(","):
                flash(row[1:-1])

        # delete pie plot image (not rendered next time entry on metrics page)
        if os.path.exists(app.config['IMAGES_FOLDER'] + "third_plot.png"):
            os.remove(app.config['IMAGES_FOLDER'] + "third_plot.png")
    return render_template('restore.html')


@app.route('/add_student', methods=['GET', 'POST'])
@check_user_logged
def add_student(code, subject):
    if request.method == 'POST':
        if 'studentslist' not in request.files:
            flash('No selected file')
            return redirect('/add_student')

        file = request.files['studentslist']
        if file.filename == '':
            flash('No selected file')
            return redirect('/add_student')

        import_file_student(file, code, subject)

    return render_template('add_student.html')


@app.route('/add_questions', methods=['GET', 'POST'])
@check_user_logged
def add_questions(code, subject):
    if request.method == 'POST':
        if 'questionslist' not in request.files:
            flash('No selected file')
            return redirect('/add_questions')

        file = request.files['questionslist']
        if file.filename == '':
            flash('No selected file')
            return redirect('/add_questions')

        import_file_questions(file, code, subject)

    return render_template('add_questions.html')


@app.route('/exam_parameters', methods=['GET', 'POST'])
@check_user_logged
def exam_parameters(code, subject):
    if request.method == 'POST':
        # all numeric field
        number_questions = request.form['number_questions']
        point_correct_answer = request.form['point_correct_answer']
        point_incorrect_answer = request.form['point_incorrect_answer']
        point_uncomplete_answer = request.form['point_uncomplete_answer']

        if point_incorrect_answer <= point_uncomplete_answer:
            flash("Point uncomplete answer must be minor of of point incorrect answer")
            return redirect('/exam_parameters')

        # call exammanager
        data_post = {
            'code': code,
            'subject': subject,
            'number_questions': number_questions,
            'point_correct_answer': point_correct_answer,
            'point_incorrect_answer': point_incorrect_answer,
            'point_uncomplete_answer': point_uncomplete_answer
        }
        response = requests.post("http://exammanager:5000/add_parameters", data=data_post)

        if response.status_code == 200:
            flash("Parameters added successfully")
            return redirect('/exam_parameters')
        if response.status_code == 500:
            flash(response.content.decode())
            return redirect('/exam_parameters')

    return render_template('exam_parameters.html')


@app.route('/get_file/<file>', methods=['GET'])
@check_user_logged
def get_file(code, subject, file):
    # retrieve static file from filesharing server
    response = requests.get("http://filesharing:8080/files/{}/{}/{}".format(code, subject, file))
    # store file locally
    with open(app.config['UPLOAD_FOLDER'] + file, "w") as f:
        f.write(response.content.decode())

    # delete file at the end of the request
    @after_this_request
    def removeFile(after_response):
        os.remove(app.config['UPLOAD_FOLDER'] + file)
        return after_response

    # trigger download from browser
    return send_from_directory(app.config['UPLOAD_FOLDER'], file)


@app.route('/logout')
@check_user_logged
def logout(code, subject):
    # delete cookie
    session.pop('prof_data')
    return redirect('/login')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)