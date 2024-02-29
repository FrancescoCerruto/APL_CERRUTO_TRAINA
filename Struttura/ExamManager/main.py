import json

from project.model import create_question, delete_all, create_parameters, creation_exam, correction_exam, \
    read_questions, read_exams, read_parameters, get_result
from project import create_app
from flask import request

app = create_app()


# add question to data set of questions
@app.route('/add_question', methods=['POST'])
def add_question():
    # request.form --> dictionary

    # numeric field
    id_question = request.form['id']
    # string field
    code = request.form['code']
    subject = request.form['subject']
    question = request.form['question']
    a1 = request.form['answer1']
    a2 = request.form['answer2']
    a3 = request.form['answer3']
    a4 = request.form['answer4']
    ca = request.form['correct_answer']
    
    # mongo require a list of string for answers and correct answers
    answers = [a1, a2, a3, a4]
    # single correct answer
    if '[' not in ca:
        correct_answer = [ca]
        response_db = create_question(id_question, code, subject, question, answers, correct_answer)
    else:
        # multiple correct answers (slice string remove '[]')
        correct_answers = [element for element in ca[1:-1].split(", ")]
        response_db = create_question(id_question, code, subject, question, answers, correct_answers)
    if response_db == -1:
        return "Duplicate entry", 400
    if response_db == -2:
        return "Error insert", 500
    return "", 200


# delete questions and student exams
@app.route('/delete_exams', methods=['POST'])
def delete_exams():
    # request.json --> dictionary

    # string field
    code = request.json['code']
    subject = request.json['subject']

    response_db = delete_all(code, subject)

    if response_db == -1:
        return "Questions and Exams empty", 400
    if response_db == -3:
        return "Error delete", 500
    return "Exam manager restored", 200


# create and store student exam
@app.route('/create_exam', methods=['POST'])
def create_exam():
    # request.form --> dictionary

    # string field
    student_code = request.form['StudentCode']
    professor_code = request.form['ProfessorCode']
    subject = request.form['Subject']

    response_db = creation_exam(student_code, professor_code, subject)
    if response_db == -1:
        return "Empty dataset to create exam", 400
    if response_db == -2:
        return "Error creation", 500
    return response_db, 200


# verify student exam
@app.route('/end_exam', methods=['POST'])
def end_exam():
    # request.form --> dictionary

    # string field
    student_code = request.form['StudentCode']
    professor_code = request.form['ProfessorCode']
    subject = request.form['Subject']
    # from string to list of dict
    answers = json.loads(request.form['Answers'])

    response_db = correction_exam(student_code, professor_code, subject, answers)
    if response_db == "Exam not found":
        return "Exam not found", 400
    if response_db == "Invalid questions":
        return "Invalid questions", 400
    if response_db == "Error correction":
        return "Error correction", 500
    return {'result': response_db}, 200


# return result student exam
@app.route('/retrieve_result', methods=['POST'])
def retrieve_result():
    # request.form --> dictionary

    # string field
    student_code = request.form['StudentCode']
    professor_code = request.form['ProfessorCode']
    subject = request.form['Subject']

    response_db = get_result(student_code, professor_code, subject)
    if response_db == -1:
        return "Exam not found", 400
    if response_db == -2:
        return "Error database", 500
    return response_db, 200


# set parameters execution of exams
@app.route('/add_parameters', methods=['POST'])
def add_parameters():
    # request.form --> dictionary

    # string field
    code = request.form['code']
    subject = request.form['subject']
    # numeric field
    number_questions = request.form['number_questions']
    point_correct_answer = request.form['point_correct_answer']
    point_incorrect_answer = request.form['point_incorrect_answer']
    point_uncomplete_answer = request.form['point_uncomplete_answer']

    response_db = create_parameters(code, subject, int(number_questions), point_correct_answer, point_incorrect_answer, point_uncomplete_answer)

    if response_db == -2:
        return "Error parameters creation", 500
    return "", 200


# return list of questions of student exam
@app.route('/retrieve_questions', methods=['POST'])
def retrieve_questions():
    # request.form --> dictionary

    # string field
    professor_code = request.form['ProfessorCode']
    subject = request.form['Subject']
    id_questions = json.loads(request.form['IdQuestions'])

    response_db = read_questions(professor_code, subject, id_questions)
    if response_db == -1:
        return "Error retrieve", 500
    return response_db, 200


# return list of all exams stored
@app.route('/return_exams', methods=['POST'])
def return_exams():
    # request.form --> dictionary

    # string field
    professor_code = request.form['ProfessorCode']
    subject = request.form['Subject']

    if "" in [professor_code, subject]:
        return "Required data", 400

    response_db = read_exams(professor_code, subject)
    if response_db == -1:
        return "Error retrieve", 500
    return response_db, 200


# return list of exam parameters
@app.route('/return_parameters', methods=['POST'])
def return_parameters():
    # request.form --> dictionary

    # string field
    professor_code = request.form['ProfessorCode']
    subject = request.form['Subject']

    response_db = read_parameters(professor_code, subject)
    if response_db == -1:
        return "Error retrieve", 500
    return response_db, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)