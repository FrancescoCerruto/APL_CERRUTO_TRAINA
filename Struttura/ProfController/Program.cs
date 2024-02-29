namespace ProfController
{
    // entry point system
    public class Program
    {
        public static void Main(string[] args)
        {
            // create and run web host
            CreateHostBuilder(args).Build().Run();
        }

        // IHostBuilder object is used to configure webhost (default settings)
        // in this case we overwrite ASPNETCORE_URLS by docker compose
        public static IHostBuilder CreateHostBuilder(string[] args) =>
            // configure services and set up the application's startup.
            Host.CreateDefaultBuilder(args)
                .UseSystemd()   //enable running linux service
                .ConfigureWebHostDefaults(webBuilder =>
                {
                    webBuilder.UseStartup<Startup>();
                });
    }
}