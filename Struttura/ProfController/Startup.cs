namespace ProfController
{
    public class Startup
    {
        // object configuration is automatically provided by ASP.NET Core's dependency injection system
        /*
         * read from appsettings.json files (key, value)
         * read from environment variables (docker passed)
         */
        public Startup(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public IConfiguration Configuration { get; }

        // This method gets called by the runtime. Use this method to add services to the container.
        public void ConfigureServices(IServiceCollection services)
        {
            // this app is am API controller --> ddd controllers to the services container
            services.AddControllers();
        }

        // This method gets called by the runtime. Use this method to configure the HTTP request pipeline.
        // what is?
        /*
         * sequence of middleware components and handlers that are invoked to handle an incoming HTTP request
         * and generate an appropriate response
         * 
         * so process, execute and reply
         */
        // env object is configured at runtime (in docker compose specify Development)
        public void Configure(IApplicationBuilder app, IWebHostEnvironment env)
        {
            // Check if the application is running in the development environment.
            if (env.IsDevelopment())
            {
                app.UseDeveloperExceptionPage();
            }

            // Enable routing middleware to route requests to endpoints.
            // how it wirks?
            /*
             * ApiController --> direttiva ApiController - questa direttiva dice al runtime che qualsiasi route http
             * in ingresso è servita da questo oggetto
             * 
             * matches the request's URL to an endpoint in the application's route table
             * 
             * The endpoint consists of information such as the controller, action method, and any route parameters.
             */
            app.UseRouting();

            // Enable authorization middleware to authenticate and authorize requests.
            app.UseAuthorization();

            // Enable endpoint routing middleware to execute endpoint and generate HTTP response.
            app.UseEndpoints(endpoints =>
            {
                endpoints.MapControllers();
            });
        }
    }
}