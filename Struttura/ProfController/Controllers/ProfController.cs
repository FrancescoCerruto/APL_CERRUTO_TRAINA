using Microsoft.AspNetCore.Mvc;
using ProfController.Database;
using ProfController.DelegatesAction;
using ServiceStack;
using ServiceStack.Redis;

namespace ProfController.Controllers
{
    // http://host:port/api/Prof/
    [Microsoft.AspNetCore.Mvc.Route("api/[controller]")]

    // direttiva usata per lo sviluppo di API
    [ApiController]
    public class ProfController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly ILogger<ProfController> _logger;
        private RedisEndpoint redis;
        private RedisClient redis_client;

        //configuration object passed with dependency injection (same as logger)
        public ProfController(IConfiguration configuration, ILogger<ProfController> logger)
        {
            _configuration = configuration;
            _logger = logger;

            /* le variabili di ambiente per la configurazione vengono passate da docker compose
             * se non esiste la key nel docker compose cerco nella entry CONNECTION_STRING del file appsettings.Development.json
             * (configurato in startup)
             */
            var host = _configuration["DBHOST"] ?? "localhost";
            var port = _configuration["DBPORT"] ?? "6379";

            redis = new RedisEndpoint { Host = host, Port = port.ToInt() };
            redis_client = new RedisClient(redis);
        }

        public delegate Task<string> MyDelegate(string prof_code, string subject); //declaring a delegate

        // /restore_system
        [HttpPost("restore_system")]
        public async Task<IActionResult> RestoreSystemAsync([FromForm] Exam exam)
        {
            // controllo se ho presente su redis qualche studente per questo esame che non hanno ancora completato
            // --> non posso resettare il sistema
            foreach (string key in redis_client.GetAllKeys())
            {
                if (redis_client.GetValue(key) == "Not completed")
                {
                    return StatusCode(400, "Exam not completed");
                }
            }
            // in future enable students to redo exam
            redis_client.RemoveAll(redis_client.GetAllKeys());

            // collect delegates
            List<Task> tasks = new List<Task>();

            // execute system restore - each delegate one call to server
            MyDelegate s = DelegateAction.delete_students;
            MyDelegate q = DelegateAction.delete_exams_mongo;
            MyDelegate e = DelegateAction.delete_exams_file;

            // create single task
            var ta1 = s(exam.ProfessorCode, exam.Subject);
            var ta2 = q(exam.ProfessorCode, exam.Subject);
            var ta3 = e(exam.ProfessorCode, exam.Subject);

            // add task to collection (and starts execution)
            tasks.Add(ta1);
            tasks.Add(ta2);
            tasks.Add(ta3);

            // wait execution
            await Task.WhenAll(tasks);

            // retrieve results
            string[] result = [ta1.Result, ta2.Result, ta3.Result];
            return Ok(result);
        }

        // /metrics
        [HttpPost("metrics")]
        public async Task<IActionResult> MetricsAsync([FromForm] Exam exam)
        {
            MyDelegate ce = DelegateAction.created_exams;
            MyDelegate fe = DelegateAction.finished_exams;
            MyDelegate pa = DelegateAction.passed_exams;
            MyDelegate pap = DelegateAction.passed_exams_percentage;
            MyDelegate fap = DelegateAction.failed_exams_percentage;
            MyDelegate avt = DelegateAction.average_exams_time;
            MyDelegate ar = DelegateAction.average_result;

            // collect delegates
            List<Task> tasks = new List<Task>();

            // create single task
            var ta1 = ce(exam.ProfessorCode, exam.Subject);
            var ta2 = fe(exam.ProfessorCode, exam.Subject);
            var ta3 = pa(exam.ProfessorCode, exam.Subject);
            var ta4 = pap(exam.ProfessorCode, exam.Subject);
            var ta5 = fap(exam.ProfessorCode, exam.Subject);
            var ta6 = avt(exam.ProfessorCode, exam.Subject);
            var ta7 = ar(exam.ProfessorCode, exam.Subject);

            // add task to collection (and starts execution)
            tasks.Add(ta1);
            tasks.Add(ta2);
            tasks.Add(ta3);
            tasks.Add(ta4);
            tasks.Add(ta5);
            tasks.Add(ta6);
            tasks.Add(ta7);

            // wait execution
            await Task.WhenAll(tasks);

            // retrieve results
            string[] result = [ta1.Result, ta2.Result, ta3.Result, ta4.Result, ta5.Result, ta6.Result, ta7.Result];
            return Ok(result);
        }
    }
}
