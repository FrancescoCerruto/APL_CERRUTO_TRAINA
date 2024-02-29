# ambiente di run
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

# ambiente di compilazione
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["ProfController.csproj", "./"]
RUN dotnet restore "ProfController.csproj"
COPY . .
WORKDIR "/src/."
RUN dotnet build "ProfController.csproj" -c Release -o /app/build

# ambiente di interpretazione
FROM build AS publish
RUN dotnet publish "ProfController.csproj" -c Release -o /app/publish

# ambiente di esecuzione
FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "ProfController.dll"]