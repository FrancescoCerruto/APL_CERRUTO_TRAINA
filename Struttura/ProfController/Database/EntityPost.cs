namespace ProfController.Database
{
    // match JSON sent by professorserver/restore_system and professorserver/metrics
    public class Exam
    {
        public string ProfessorCode { get; set; }
        public string Subject { get; set; }
    }
}
