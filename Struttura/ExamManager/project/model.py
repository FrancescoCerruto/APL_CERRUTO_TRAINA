import json
import random
from project import db
from datetime import datetime


# each question is linked to prof code and subject -->
# easy retrieval on exam creation
class Question(db.Document):
    id_question = db.IntField()
    prof_code = db.StringField()
    subject = db.StringField()
    text = db.StringField()
    answers = db.ListField(db.StringField())
    correct_answers = db.ListField(db.StringField())


# each set of parameters is linked to prof code and subject -->
# easy retrieval on exam correction
class ExamParameters(db.Document):
    prof_code = db.StringField()
    subject = db.StringField()
    # execution parameter
    number_questions = db.IntField()
    # correction parameter
    # correction policy
    # if there is an incorrect answer --> incorrect question
    # if number of given response is equal to required number of response --> correct question
    # if number of given response is minor to required number of response --> incorrect question
    # if number of given response is 0 --> uncomplete question
    point_correct_answer = db.FloatField()
    point_incorrect_answer = db.FloatField()
    point_uncomplete_answer = db.FloatField()


# student exam is linked to prof code and subject -->
# easy retrieval on metrics generation
class StudentExam(db.Document):
    student_code = db.StringField()
    prof_code = db.StringField()
    subject = db.StringField()
    id_questions = db.ListField(db.IntField())
    answers = db.ListField(db.StringField())
    result = db.FloatField()
    completed = db.BooleanField()
    start_exam = db.DateTimeField()
    end_exam = db.DateTimeField()


# create question
def create_question(id_question, prof_code, subject, text, answers, correct_answers):
    try:
        # check if same question is already stored --> error duplicate
        record = Question.objects(id_question=id_question, prof_code=prof_code, subject=subject, text=text,
                                  answers=answers, correct_answers=correct_answers).first()
        if not record:
            Question(id_question=id_question, prof_code=prof_code, subject=subject, text=text, answers=answers,
                     correct_answers=correct_answers).save()
            return 0
        return -1
    except Exception as e:
        print(str(e))
        return -2


# set parameters execution and correction
def create_parameters(prof_code, subject, number_questions, point_correct_answer, point_incorrect_answer,
                      point_uncomplete_answer):
    try:
        # check if parameters are already set --> update
        record = ExamParameters.objects(prof_code=prof_code, subject=subject).first()
        if not record:
            count = len(Question.objects(prof_code=prof_code, subject=subject))
            # professor could save a data set of questions of length n and require an exam of m questions (m > n) -->
            # duplicated questions on same exams
            ExamParameters(prof_code=prof_code, subject=subject, number_questions=min(count, number_questions),
                           point_correct_answer=point_correct_answer, point_incorrect_answer=point_incorrect_answer,
                           point_uncomplete_answer=point_uncomplete_answer).save()
            return 0
        else:
            record.delete()
            count = len(Question.objects(prof_code=prof_code, subject=subject))
            ExamParameters(prof_code=prof_code, subject=subject, number_questions=min(count, number_questions),
                           point_correct_answer=point_correct_answer, point_incorrect_answer=point_incorrect_answer,
                           point_uncomplete_answer=point_uncomplete_answer).save()
            return 0
    except Exception as e:
        print(str(e))
        return -2


# create exam
def creation_exam(student_code, prof_code, subject):
    try:
        # check if prof stored questions and parameters --> error
        record_parameters = ExamParameters.objects(prof_code=prof_code, subject=subject).first()
        record_question = Question.objects(prof_code=prof_code, subject=subject).first()
        if (not record_parameters) or (not record_question):
            return -1
        else:
            # retrieve number of questions
            num_questions = record_parameters['number_questions']

            # generate n random id of questions
            count = len(Question.objects(prof_code=prof_code, subject=subject))
            list_index = random.sample(range(1, count+1), num_questions)

            # create exam
            list_questions = []
            response_json = []
            # for each id
            for i in range(num_questions):
                # retrieve question
                record = Question.objects(id_question=list_index[i], prof_code=prof_code, subject=subject).first()

                # store inside student exam only id question
                list_questions.append(record['id_question'])

                # return at student only id (for correction), text and answers
                response_json.append({'id_question': record['id_question'], 'text': record['text'], 'answers': record['answers']})

            # save exam
            StudentExam(prof_code=prof_code, subject=subject, student_code=student_code, id_questions=list_questions, answers=[], result=0, completed=False, start_exam=datetime.utcnow, end_exam=datetime.utcnow).save()
            return {'questions': response_json}
    except Exception as e:
        print(str(e))
        return -2


# verify exam
def correction_exam(student_code, prof_code, subject, answers):
    try:
        # retrieve student exam
        record_exam = StudentExam.objects(student_code=student_code, prof_code=prof_code, subject=subject).first()
        if not record_exam:
            return "Exam not found"
        else:
            id_questions = record_exam['id_questions']
            start_exam = record_exam['start_exam']

            # retrieve parameters correction
            record_parameters = ExamParameters.objects(prof_code=prof_code, subject=subject).first()
            point_correct_answer = record_parameters['point_correct_answer']
            point_incorrect_answer = record_parameters['point_incorrect_answer']
            point_uncomplete_answer = record_parameters['point_uncomplete_answer']

            # correction
            result = 0.0
            answers_db = []

            # for each question of exam
            for question in answers:
                id_question = question['id_question']

                # bypass correction
                if len(question['answers']) == 0:
                    result = result - point_uncomplete_answer
                else:
                    # retrieve correct answers
                    record_question = Question.objects(id_question=id_question, prof_code=prof_code, subject=subject).first()
                    correct_answers = record_question['correct_answers']

                    correct = 0
                    error = 0

                    # for each response given by student to this question
                    for response in question['answers']:
                        if response in correct_answers:
                            correct = correct + 1
                        else:
                            error = error + 1

                    # correction policy
                    # if there is an incorrect answer --> incorrect question
                    # if number of given response is equal to required number of response --> correct question
                    # if number of given response is minor to required number of response --> incorrect question
                    # if number of given response is 0 --> uncomplete question
                    if error > 0:
                        result = result - point_incorrect_answer
                    else:
                        if len(correct_answers) == correct:
                            result = result + point_correct_answer
                        else:
                            result = result - point_incorrect_answer
                # append answers to array
                answers_db.append(json.dumps(question))
            # store response of student
            record_exam.delete()
            StudentExam(prof_code=prof_code, subject=subject, student_code=student_code, id_questions=id_questions, answers=answers_db, result=result, completed=True, start_exam=start_exam, end_exam=datetime.utcnow).save()
            return result
    except Exception as e:
        print(str(e))
        return "Error correction"


# delete questions and students
def delete_all(prof_code, subject):
    try:
        record_questions = Question.objects(prof_code=prof_code, subject=subject).first()
        if record_questions:
            # if there is an exam not completed we can't delete questions (c# stop execution before we call exammanger)
            record_students = StudentExam.objects(prof_code=prof_code, subject=subject, completed=False).first()
            if not record_students:
                Question.objects(prof_code=prof_code, subject=subject).delete()
                StudentExam.objects(prof_code=prof_code, subject=subject, completed=True).delete()
                ExamParameters.objects(prof_code=prof_code, subject=subject).delete()
                return 0
            return -1
        return -1
    except Exception as e:
        print(str(e))
        return -3


# return list of questions of student exam (match id)
def read_questions(professor_code, subject, id_questions):
    try:
        questions_response = []
        for id_required in id_questions:
            # retrieve question
            record_question = Question.objects(id_question=id_required, prof_code=professor_code, subject=subject).first()
            questions_response.append({
                'id_question': record_question['id_question'],
                'text': record_question['text'],
                'answers': record_question['answers'],
                'correct_answers': record_question['correct_answers'],
            })
        return {'questions': questions_response}
    except Exception as e:
        print(str(e))
        return -1


# return list of students exams
def read_exams(professor_code, subject):
    try:
        exams_response = []
        record_exams = StudentExam.objects(prof_code=professor_code, subject=subject)
        for exam in record_exams:
            exams_response.append({
                'student_code': exam['student_code'],
                'id_questions': exam['id_questions'],
                'answers': exam['answers'],
                'result': exam['result'],
                'completed': exam['completed'],
                'start_exam': exam['start_exam'],
                'end_exam': exam['end_exam']
            })

        return {'exams': exams_response}
    except Exception as e:
        print(str(e))
        return -1


# return exam parameters
def read_parameters(professor_code, subject):
    try:
        record_parameters = ExamParameters.objects(prof_code=professor_code, subject=subject).first()
        if not record_parameters:
            return -1
        parameters_response = {
            'number_questions': record_parameters['number_questions'],
            'point_correct_answer': record_parameters['point_correct_answer'],
            'point_incorrect_answer': record_parameters['point_incorrect_answer'],
            'point_uncomplete_answer': record_parameters['point_uncomplete_answer']
        }
        return {'parameters': parameters_response}
    except Exception as e:
        print(str(e))
        return -1


# return result of student exam (match id)
def get_result(student_code, professor_code, subject):
    try:
        record = StudentExam.objects(prof_code=professor_code, subject=subject, student_code=student_code).first()
        if not record:
            return -1
        else:
            return {'result': record['result']}
    except Exception as e:
        print(str(e))
        return -2