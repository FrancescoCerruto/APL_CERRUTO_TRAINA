using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using ServiceStack;
using ServiceStack.Redis;
using ServiceStack.Web;
using StudentController.Database;
using StudentController.DelegatesAction;
using System.Net;
using static ServiceStack.Diagnostics.Events;
using System.Text;

namespace StudentController.Controllers
{
    // http://host:port/api/Student/
    [Microsoft.AspNetCore.Mvc.Route("api/[controller]")]

    // direttiva usata per lo sviluppo di API
    [ApiController]
    public class StudentController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<StudentController> _logger;
        private RedisEndpoint redis;
        private RedisClient redis_client;

        //configuration object passed with dependency injection (same as logger)
        public StudentController(IConfiguration configuration, ILogger<StudentController> logger)
        {
            _configuration = configuration;
            _logger = logger;

            var host = _configuration["DBHOST"] ?? "localhost";
            var port = _configuration["DBPORT"] ?? "6379";

            redis = new RedisEndpoint { Host = host, Port = port.ToInt() };
            redis_client = new RedisClient(redis);
        }

        public delegate Task<string> MyDelegate(string student_code, string prof_code, string subject, List<Answer> answers); //declaring a delegate
        
        private async Task<IActionResult> CreateExam([FromForm] Student student)
        {
            // call exammanager
            var values = new Dictionary<string, string>
                {
                    { "StudentCode", student.StudentCode },
                    { "ProfessorCode", student.ProfessorCode },
                    { "Subject", student.Subject }
                 };
            // html form data --> su python farò request.form[]
            var content = new FormUrlEncodedContent(values);

            // send request
            var response = await DelegateAction.client.PostAsync("http://exammanager:5000/create_exam", content);

            // if exam manager not create exam (status code 200) --> return
            if (response.StatusCode != HttpStatusCode.OK)
            {
                return StatusCode((int)response.StatusCode, await response.Content.ReadAsStringAsync());
            }

            // from string to object
            Exam exam = JsonConvert.DeserializeObject<Exam>(await response.Content.ReadAsStringAsync());
            
            // enable student redo exams until restore system
            redis_client.SetValue(student.StudentCode, "Not completed");
            
            return StatusCode(200, JsonConvert.SerializeObject(exam));
        }

        // /check_exam
        [HttpPost("check_exam")]
        public async Task<IActionResult> CheckExamAsync([FromForm] Student student)
        {
            // controllo se ho presente su redis lo studente --> ha già creato un compito
            if (redis_client.ContainsKey(student.StudentCode))
            {
                return StatusCode(400, "Exam already created");
            }
            else
            {
                return await CreateExam(student);
            }
        }

        // /end_exam
        [HttpPost("end_exam")]
        public async Task<IActionResult> EndExamAsync([FromForm] Upload upload)
        {
            // collect delegates
            List<Task> tasks = new List<Task>();  

            // declare delegates
            MyDelegate d_end = DelegateAction.end_exam;
            MyDelegate d_upload = DelegateAction.upload_exam;

            // create single task
            var ta1 = d_end(upload.StudentCode, upload.ProfessorCode, upload.Subject, JsonConvert.DeserializeObject<List<Answer>>(upload.Answers));
            var ta2 = d_upload(upload.StudentCode, upload.ProfessorCode, upload.Subject, JsonConvert.DeserializeObject<List<Answer>>(upload.Answers));
            
            // add task to collection (and start execution)
            tasks.Add(ta1);
            tasks.Add(ta2);

            // wait execution
            await Task.WhenAll(tasks);

            // store result in redis
            redis_client.SetValue(upload.StudentCode, ta1.Result);

            // update file with result
            var values = new Dictionary<string, string>
            {
                { "StudentCode", upload.StudentCode },
                { "ProfessorCode", upload.ProfessorCode },
                { "Subject", upload.Subject},
                { "Result", ta1.Result },
            };

            // prepare request
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://filesharing:8080/update"),
                Content = new StringContent(JsonConvert.SerializeObject(values), Encoding.UTF8, "application/json")
            };
            // send request and return response
            var response = await DelegateAction.client.SendAsync(request);

            // retrieve results
            string[] result = [ta1.Result, ta2.Result, await response.Content.ReadAsStringAsync()];
            return Ok(result);
        }

        // /retrieve_result
        [HttpPost("retrieve_result")]
        public async Task<IActionResult> RetrieveResultAsync([FromForm] Student student)
        {
            // retrieve result
            redis_client.GetValue(student.StudentCode);
            return Ok(redis_client.GetValue(student.StudentCode));
        }
    }
}
