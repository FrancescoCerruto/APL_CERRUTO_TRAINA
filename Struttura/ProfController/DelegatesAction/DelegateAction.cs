using Newtonsoft.Json;
using System.Text;

namespace ProfController.DelegatesAction
{
    public class DelegateAction
    {
        private static readonly HttpClient client = new HttpClient();

        public async static Task<string> delete_students(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start delete_students");
            // create body request
            var data_post = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", prof_subject }
            };

            // create http request
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Delete,
                RequestUri = new Uri("http://authenticationserver:80/api/User/delete_all_students"),
                // from string to http body
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            // send request and retrieve response
            var response = await client.SendAsync(request);
            var responseString = await response.Content.ReadAsStringAsync();
            Console.WriteLine("End delete_students");
            return responseString;
        }

        public async static Task<string> delete_exams_mongo(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start delete_exams_mongo");
            // create body request
            var data_post = new Dictionary<string, string>
            {
                { "code", prof_code },
                { "subject", prof_subject }
            };

            // create http request
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://exammanager:5000/delete_exams"),
                // from string to http body
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            // send request and retrieve response
            var response = await client.SendAsync(request);
            var responseString = await response.Content.ReadAsStringAsync();
            Console.WriteLine("End delete_exams_mongo");
            return responseString;
        }

        public async static Task<string> delete_exams_file(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start delete_exams_file");
            // create body request
            var data_post = new Dictionary<string, string>
            {
                { "code", prof_code },
                { "subject", prof_subject }
            };

            // create http request
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://filesharing:8080/delete_exams"),
                // from string to http body
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            // send request and retrieve response
            var response = await client.SendAsync(request);
            var responseString = await response.Content.ReadAsStringAsync();
            Console.WriteLine("End delete_exams_file");
            return responseString;
        }

        public async static Task<string> created_exams(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start created_exams");

            // create body request
            var data_post = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", prof_subject }
            };

            // create http request
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://metricscontroller:5000/created_exams"),
                // from string to http body
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            // send request and retrieve response
            var response = await client.SendAsync(request);
            var responseString = await response.Content.ReadAsStringAsync();
            Console.WriteLine("End created_exams");
            return responseString;
        }

        public async static Task<string> finished_exams(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start finished_exams");
            var data_post = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", prof_subject }
            };

            // call metrics and return response
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://metricscontroller:5000/finished_exams"),
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            var response = await client.SendAsync(request);
            var responseString = await response.Content.ReadAsStringAsync();

            Console.WriteLine("End finished_exams");
            return responseString;
        }

        public async static Task<string> passed_exams(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start passed_exams");
            var data_post = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", prof_subject }
            };

            // call metrics and return response
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://metricscontroller:5000/passed_exams"),
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            var response = await client.SendAsync(request);
            var responseString = await response.Content.ReadAsStringAsync();

            Console.WriteLine("End passed_exams");
            return responseString;
        }

        public async static Task<string> passed_exams_percentage(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start passed_exams_percentage");
            var data_post = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", prof_subject }
            };

            // call metrics and return response
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://metricscontroller:5000/passed_exams_percentage"),
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            var response = await client.SendAsync(request);
            var responseString = await response.Content.ReadAsStringAsync();

            Console.WriteLine("End passed_exams_percentage");
            return responseString;
        }

        public async static Task<string> failed_exams_percentage(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start failed_exams_percentage");
            var data_post = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", prof_subject }
            };

            // call metrics and return response
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://metricscontroller:5000/failed_exams_percentage"),
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            var response = await client.SendAsync(request);

            var responseString = await response.Content.ReadAsStringAsync();

            Console.WriteLine("End failed_exams_percentage");
            return responseString;
        }

        public async static Task<string> average_exams_time(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start average_exams_time");
            var data_post = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", prof_subject }
            };

            // call metrics and return response
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://metricscontroller:5000/average_exams_time"),
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            var response = await client.SendAsync(request);

            Console.WriteLine("End average_exams_time");
            return await response.Content.ReadAsStringAsync();
        }

        public async static Task<string> average_result(string prof_code, string prof_subject)
        {
            Console.WriteLine("Start average_result");
            var data_post = new Dictionary<string, string>
            {
                { "ProfessorCode", prof_code },
                { "Subject", prof_subject }
            };

            // call metrics and return response
            var request = new HttpRequestMessage
            {
                Method = HttpMethod.Post,
                RequestUri = new Uri("http://metricscontroller:5000/average_result"),
                Content = new StringContent(JsonConvert.SerializeObject(data_post), Encoding.UTF8, "application/json")
            };

            var response = await client.SendAsync(request);

            Console.WriteLine("End average_result");
            return await response.Content.ReadAsStringAsync();
        }
    }
}
