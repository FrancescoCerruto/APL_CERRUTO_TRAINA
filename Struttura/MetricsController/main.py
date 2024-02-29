import json
import requests
from datetime import datetime
from project import create_app
from flask import request

app = create_app()


# return number of stored exams
@app.route('/created_exams', methods=['POST'])
def created_exams():
    # request.json --> dictionary

    # string field
    code = request.json['ProfessorCode']
    subject = request.json['Subject']

    # retrieve all exams
    data_post = {
        'ProfessorCode': code,
        'Subject': subject,
    }
    response = requests.post("http://exammanager:5000/return_exams", data=data_post)

    if response.status_code == 200:
        response_json = json.loads(response.content.decode())
        if len(response_json) > 0:
            return str(len(response_json['exams'])), 200
        return str(0), 200
    return str(0), 500


# return number of completed exams
@app.route('/finished_exams', methods=['POST'])
def finished_exams():
    # request.json --> dictionary

    # string field
    code = request.json['ProfessorCode']
    subject = request.json['Subject']

    # retrieve all exams
    data_post = {
        'ProfessorCode': code,
        'Subject': subject,
    }
    response = requests.post("http://exammanager:5000/return_exams", data=data_post)

    if response.status_code == 200:
        # iterate for each exam and count only completed exams
        exams = json.loads(response.content.decode())
        count = 0
        for element in exams['exams']:
            if element['completed']:
                count = count + 1
        return str(count), 200
    return str(0), 500


# return number of passed exams
@app.route('/passed_exams', methods=['POST'])
def passed_exams():
    # request.json --> dictionary

    # string field
    code = request.json['ProfessorCode']
    subject = request.json['Subject']

    # retrieve all exams
    data_post = {
        'ProfessorCode': code,
        'Subject': subject,
    }
    response_exams = requests.post("http://exammanager:5000/return_exams", data=data_post)

    if response_exams.status_code == 200:
        exams = json.loads(response_exams.content.decode())

        # retrieve parameters
        response_parameters = requests.post("http://exammanager:5000/return_parameters", data=data_post)
        if response_parameters.status_code == 200:
            parameters_json = json.loads(response_parameters.content.decode())['parameters']

            # iterate for each exam and count only passed exams (result > "quorum")
            count = 0
            for element in exams['exams']:
                if element['result'] >= float(parameters_json['number_questions']) / 2.0 * parameters_json['point_correct_answer']:
                    count = count + 1
            return str(count), 200
    return str(0), 500


# return percentage of passed exams
@app.route('/passed_exams_percentage', methods=['POST'])
def passed_exams_percentage():
    # request.json --> dictionary

    # string field
    code = request.json['ProfessorCode']
    subject = request.json['Subject']

    # retrieve all exams
    data_post = {
        'ProfessorCode': code,
        'Subject': subject,
    }
    response_exams = requests.post("http://exammanager:5000/return_exams", data=data_post)

    if response_exams.status_code == 200:
        exams = json.loads(response_exams.content.decode())

        # retrieve parameters
        response_parameters = requests.post("http://exammanager:5000/return_parameters", data=data_post)
        if response_parameters.status_code == 200:
            parameters = json.loads(response_parameters.content.decode())['parameters']

            count = 0
            completed_count = 0

            # iterate for each exam and count only completed and passed exams
            for element in exams['exams']:
                if element['completed']:
                    completed_count = completed_count + 1
                if element['result'] >= float(parameters['number_questions']) / 2.0 * parameters['point_correct_answer']:
                    count = count + 1

            # control required for division by 0
            if completed_count == 0:
                return str(0), 200

            passed_percentage = 100.0 - (float(completed_count) - float(count)) / float(completed_count) * 100.0
            return str(passed_percentage), 200
    return str(0), 500


# return percentage of failed exams
@app.route('/failed_exams_percentage', methods=['POST'])
def failed_exams_percentage():
    # request.json --> dictionary

    # string field
    code = request.json['ProfessorCode']
    subject = request.json['Subject']

    # retrieve all exams
    data_post = {
        'ProfessorCode': code,
        'Subject': subject,
    }
    response_exams = requests.post("http://exammanager:5000/return_exams", data=data_post)

    if response_exams.status_code == 200:
        exams = json.loads(response_exams.content.decode())

        # retrieve parameters
        response_parameters = requests.post("http://exammanager:5000/return_parameters", data=data_post)
        if response_parameters.status_code == 200:
            parameters = json.loads(response_parameters.content.decode())['parameters']

            count = 0
            completed_count = 0

            # iterate for each exam and count only completed and passed exams
            for element in exams['exams']:
                if element['completed']:
                    completed_count = completed_count + 1
                if element['result'] >= float(parameters['number_questions']) / 2.0 * parameters['point_correct_answer']:
                    count = count + 1

            # control required for division by 0
            if completed_count == 0:
                return str(0), 200

            failed_percentage = (float(completed_count) - float(count)) / float(completed_count) * 100.0
            return str(failed_percentage), 200
    return str(0), 500


# return local time delivery and average time delivery
@app.route('/average_exams_time', methods=['POST'])
def average_exams_time():
    # request.json --> dictionary

    # string field
    code = request.json['ProfessorCode']
    subject = request.json['Subject']

    # retrieve all exams
    data_post = {
        'ProfessorCode': code,
        'Subject': subject,
    }
    response = requests.post("http://exammanager:5000/return_exams", data=data_post)

    if response.status_code == 200:
        exams = json.loads(response.content.decode())

        # iterate for each exam and consider only completed exams
        count = 0.0
        completed_count = 0
        time_students = []
        for element in exams['exams']:
            if element['completed']:
                # store local time
                time_students.append((datetime.strptime(element['end_exam'], '%a, %d %b %Y %H:%M:%S GMT') - datetime.strptime(element['start_exam'], '%a, %d %b %Y %H:%M:%S GMT')).total_seconds())

                # add local time for average
                count = count + (datetime.strptime(element['end_exam'], '%a, %d %b %Y %H:%M:%S GMT') - datetime.strptime(element['start_exam'], '%a, %d %b %Y %H:%M:%S GMT')).total_seconds()
                completed_count = completed_count + 1

        if completed_count == 0:
            response = {
                'single_time': time_students,
                'average_time': 0
            }
            return response, 200

        response = {
            'single_time': time_students,
            'average_time': count / completed_count
        }
        return response, 200
    return str(0), 500


# return local result and average result
@app.route('/average_result', methods=['POST'])
def average_result():
    # request.json --> dictionary

    # string field
    code = request.json['ProfessorCode']
    subject = request.json['Subject']

    # retrieve all exams
    data_post = {
        'ProfessorCode': code,
        'Subject': subject,
    }
    response = requests.post("http://exammanager:5000/return_exams", data=data_post)

    if response.status_code == 200:
        exams = json.loads(response.content.decode())

        # iterate for each exam and count only completed exams
        count = 0.0
        completed_count = 0
        result_students = []
        for element in exams['exams']:
            if element['completed']:
                # store local result
                result_students.append(element['result'])

                # add local result for average
                count = count + element['result']
                completed_count = completed_count + 1

        if completed_count == 0:
            response = {
                'single_result': result_students,
                'average_result': 0
            }
            return response, 200

        response = {
            'single_result': result_students,
            'average_result': count / completed_count
        }
        return response, 200
    return str(0), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)