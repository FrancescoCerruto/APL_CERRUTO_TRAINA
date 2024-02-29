namespace AuthenticationServer.Database
{
    // map from request body to c# object

    // map data sent from professorserver/restore (under c# delegates professorcontroller/restore_system)
    public class Exam
    {
        public string ProfessorCode { get; set; }
        public string Subject { get; set; }
    }

    // map data sent from professorserver/register or professorserver/login
    public class Professor
    {
        public string Code { get; set; }
        public string Password { get; set; }
        public string Subject { get; set; }
    }

    // map data sent from professorserver/add_student or studentserver/login
    public class Student
    {
        public string StudentCode { get; set; }
        public string ProfessorCode { get; set; }
        public string Subject { get; set; }
    }
}
