namespace StudentController.Database
{
    // match json - model data sent from exammanager/create_exam
    /*
     * 'id_question': int,
     * 'text': string,
     * 'answers': List<String>,
     */
    public class Question
    {
        public int id_question { get; set; }
        public string text { get; set; }
        public List<object> answers { get; set; }
    }

    // collect response of exammanager/create_exam that return a List<Question>
    public class Exam
    {
        public List<Question> questions { get; set; }
    }

    // match json - model data sent from exammanager/retrieve_questions
    /*
     * 'id_question': int,
     * 'text': string,
     * 'answers': List<String>,
     * 'correct_answers': List<String>,
     */
    public class UploadQuestion
    {
        public int id_question { get; set; }
        public string text { get; set; }
        public List<object> answers { get; set; }
        public List<object> correct_answers { get; set; }
    }

    // collect response of exammanager/retrieve_questions that return a List<UploadQuestion>
    public class ResponseQuestion
    {
        public List<UploadQuestion> questions { get; set; }
    }

    // match json - model data sent from studentserver/execute_exam (single question)
    /*
     * 'id_question': int,
     * 'answers': List<String>,
     */
    public class Answer
    {
        public int id_question { get; set; }
        public List<object> answers { get; set; }

    }

    // match json - model data sent from studentserver/execute_exam (all data)
    /*
     * 'StudentCode': string,
     * 'ProfessorCode': string,
     * 'Subject': string,
     * 'Subject': List<String>,
     */
    public class Upload
    {
        public string StudentCode { get; set; }
        public string ProfessorCode { get; set; }
        public string Subject { get; set; }
        public string Answers { get; set; }
    }

    // match json data sent from exammanager/end_exam
    /*
     * 'result': double,
     */
    public class Result
    {
        public double result { get; set; }
    }

    // match json data sent from studentserver/create_exam and studentserver/retrieve_result
    public class Student
    {
        public string StudentCode { get; set; }
        public string ProfessorCode { get; set; }
        public string Subject { get; set; }
    }
}
