using AuthenticationServer.Database;
using Dapper;
using Microsoft.AspNetCore.Mvc;
using MySql.Data.MySqlClient;
using System.Data;

namespace AuthenticationServer.Controllers
{
    // http://host:port/api/User/
    [Route("api/[controller]")]

    // direttiva usata per lo sviluppo di API
    [ApiController]
    public class UserController : ControllerBase
    {
        private readonly IConfiguration _configuration;
        private readonly string connString;
        private readonly ILogger<UserController> _logger;

        //configuration object passed with dependency injection (same as logger)
        public UserController(IConfiguration configuration, ILogger<UserController> logger)
        {
            _configuration = configuration;
            _logger = logger;

            /* le variabili di ambiente per la configurazione vengono passate da docker compose
             * se non esiste la key nel docker compose cerco nella entry CONNECTION_STRING del file appsettings.Development.json
             * (configurato in startup)
             */
            var host = _configuration["DBHOST"] ?? "localhost";
            var port = _configuration["DBPORT"] ?? "3306";
            var password = _configuration["MYSQL_PASSWORD"] ?? _configuration.GetConnectionString("MYSQL_PASSWORD");
            var userid = _configuration["MYSQL_USER"] ?? _configuration.GetConnectionString("MYSQL_USER");
            var usersDataBase = _configuration["MYSQL_DATABASE"] ?? _configuration.GetConnectionString("MYSQL_DATABASE");

            // string interpolation
            connString = $"server={host}; userid={userid};pwd={password};port={port};database={usersDataBase}";
        }

        /*
         * Difference between FromForm and FromBody
         * 
         * When you use [FromBody], the data is expected to be in the request body,
         * typically in a JSON or XML format.
         * 
         * When you use [FromForm], the data is expected to be sent as form-urlencoded data,
         * often used in HTML forms.
        */

        // /authenticate_student
        [HttpPost("authenticate_student")]
        // we made a post request so user data is not visible
        public async Task<IActionResult> AuthenticateStudentAsync([FromForm] Student student)
        {
            var users = new List<Student>();
            try
            {
                // parametrized query (Dapper)
                string query = @"SELECT student_code, professor_code, subject FROM student WHERE student_code = @student_code AND professor_code = @professor_code AND subject = @subject";
                
                // create dynamic parameters dictionary
                var param = new DynamicParameters();
                param.Add("@student_code", student.StudentCode);
                param.Add("@professor_code", student.ProfessorCode);
                param.Add("@subject", student.Subject);

                // open connection
                using (var connection = new MySqlConnection(connString))
                {
                    // Dapper library --> from query result to object
                    var result = await connection.QueryAsync<Student>(query, param, null, null, CommandType.Text);
                    // from IEnumerable (iterable type) to List 
                    users = result.ToList();
                }
                if (users.Count == 1)
                {
                    // status code 200
                    return Ok();
                }
                else
                {
                    // status code 404
                    return NotFound();
                }
            }
            catch (Exception e)
            {
                return StatusCode(500, "Database error");
            }
        }

        // /add_student
        [HttpPost("add_student")]
        public async Task<IActionResult> AddStudentAsync([FromForm] Student student)
        {
            var newUser = new Student();
            try
            {
                // parametrized query (Dapper)
                string query = @"INSERT INTO student (student_code, professor_code, subject) VALUES (@student_code, @professor_code, @subject)";

                // create dynamic parameters dictionary
                var param = new DynamicParameters();
                param.Add("@student_code", student.StudentCode);
                param.Add("@professor_code", student.ProfessorCode);
                param.Add("@subject", student.Subject);

                // open connection
                using (var connection = new MySqlConnection(connString))
                {
                    // result = number of row affected from query (1)
                    var result = await connection.ExecuteAsync(query, param, null, null, CommandType.Text);
                    if (result > 0)
                    {
                        newUser = student;
                    }
                }
                if (newUser != null)
                {
                    // status code 200
                    return Ok();
                }
                else
                {
                    // status code 400
                    return BadRequest("Unable To Insert Student");
                }
            }
            catch (Exception e)
            {
                return StatusCode(500, "Database error");
            }
        }

        [HttpDelete("delete_all_students")]
        public async Task<IActionResult> DeleteAllStudentsAsync([FromBody] Exam exam)
        {
            try
            {
                // parametrized query (Dapper)
                string query = @"DELETE FROM student WHERE subject = @subject AND professor_code = @professor_code";

                // create dynamic parameters dictionary
                var param = new DynamicParameters();
                param.Add("@subject", exam.Subject);
                param.Add("@professor_code", exam.ProfessorCode);

                // open connection
                using (var connection = new MySqlConnection(connString))
                {
                    // result = number of row affected from query (n)
                    var result = await connection.ExecuteAsync(query, param, null, null, CommandType.Text);
                    if (result > 0)
                    {
                        // status code 200
                        return Ok("All students deleted successfully");
                    }
                    else
                    {
                        // status code 400
                        return StatusCode(400, "Empty student table");
                    }
                }
            }
            catch (Exception)
            {
                // status code 500
                return StatusCode(500, "Database error");
            }
        }

        // /authenticate_professor
        [HttpPost("authenticate_professor")]
        public async Task<IActionResult> AuthenticateProfessorAsync([FromForm] Professor professor)
        {
            var users = new List<Professor>();
            try
            {
                // parametrized query (Dapper)
                string query = @"SELECT code, password, subject FROM professor WHERE code = @code AND password = @password AND subject = @subject";

                // create dynamic parameters dictionary
                var param = new DynamicParameters();
                param.Add("@code", professor.Code);
                param.Add("@password", professor.Password);
                param.Add("@subject", professor.Subject);

                // open connection
                using (var connection = new MySqlConnection(connString))
                {
                    // Dapper library --> from query result to object
                    var result = await connection.QueryAsync<Professor>(query, param, null, null, CommandType.Text);
                    users = result.ToList();
                }
                if (users.Count == 1)
                {
                    // status code 200
                    return Ok();
                }
                else
                {
                    // status code 404
                    return NotFound();
                }
            }
            catch (Exception e)
            {
                return StatusCode(500, "Database error");
            }
        }

        // /add_professor
        [HttpPost("add_professor")]
        public async Task<IActionResult> AddProfessorAsync([FromForm] Professor professor)
        {
            var newUser = new Professor();
            try
            {
                // parametrized query (Dapper)
                string query = @"INSERT INTO professor (code, password, subject) VALUES (@code, @password, @subject)";

                // create dynamic parameters dictionary
                var param = new DynamicParameters();
                param.Add("@code", professor.Code);
                param.Add("@password", professor.Password);
                param.Add("@subject", professor.Subject);
                
                // open connection
                using (var connection = new MySqlConnection(connString))
                {
                    // result = number of row affected from query (1)
                    var result = await connection.ExecuteAsync(query, param, null, null, CommandType.Text);
                    if (result > 0)
                    {
                        newUser = professor;
                    }
                }
                if (newUser != null)
                {
                    // status code 200
                    return Ok();
                }
                else
                {
                    // status code 400
                    return BadRequest("Unable To Insert Professor");
                }
            }
            catch (Exception e)
            {
                // status code 500
                return StatusCode(500, "Database error");
            }
        }
    }
}
