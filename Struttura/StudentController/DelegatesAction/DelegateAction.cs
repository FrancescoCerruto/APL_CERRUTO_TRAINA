using Newtonsoft.Json;
using StudentController.Database;
using System.Net;
using System.Text;


namespace StudentController.DelegatesAction
{
    public class DelegateAction
    {
        public static readonly HttpClient client = new HttpClient();

        public async static Task<string> end_exam(string student_code, string prof_code, string subject, List<Answer> answers)
        {
            Console.WriteLine("Start end_exam");
            // call exammanager
            var values = new Dictionary<string, string>
            {
                { "StudentCode", student_code },
                { "ProfessorCode", prof_code },
                { "Subject", subject },
                { "Answers", JsonConvert.SerializeObject(answers) }
            };
            // html form data --> su python farò request.form[]
            var content = new FormUrlEncodedContent(values);
            // send request
            var response = await client.PostAsync("http://exammanager:5000/end_exam", content);
            
            if (response.StatusCode != HttpStatusCode.OK)
            {
                return await response.Content.ReadAsStringAsync();
            }

            // prepare response
            Result result = JsonConvert.DeserializeObject<Result>(await response.Content.ReadAsStringAsync());
            Console.WriteLine("End end_exam");
            return "Your result is " + result.result.ToString();
        }

        public async static Task<string> upload_exam(string student_code, string prof_code, string subject, List<Answer> answers)
        {
            Console.WriteLine("Start upload_exam");
            // retrieve questions from exam anager (esame già creato in precedenza quindi ottengo risposta)
            List<int> id_questions = new List<int>();
            foreach (Answer answer in answers)
            {
                id_questions.Add(answer.id_question);
            }
            var values = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", subject },
                { "IdQuestions", JsonConvert.SerializeObject(id_questions) }
            };
            // html form data --> su python farò request.form[]
            var content = new FormUrlEncodedContent(values);
            // send request
            var response = await client.PostAsync("http://exammanager:5000/retrieve_questions", content);
            // from string to object
            ResponseQuestion questions = JsonConvert.DeserializeObject<ResponseQuestion>(await response.Content.ReadAsStringAsync());
         
            // call filesharing
            values = new Dictionary<string, string>
            {
                { "StudentCode", student_code },
                { "ProfessorCode", prof_code },
                { "Subject", subject },
                { "Answers", JsonConvert.SerializeObject(answers) },
                { "Questions", JsonConvert.SerializeObject(questions.questions) },
            };

            // prepare request
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://filesharing:8080/upload"),
                // su python farò request.json[]
                Content = new StringContent(JsonConvert.SerializeObject(values), Encoding.UTF8, "application/json")
            };
            // send request and return response
            response = await client.SendAsync(request);
            Console.WriteLine("End upload_exam");
            return await response.Content.ReadAsStringAsync();
        }
    }
}
