#import python
FROM python:3.8

#dipendenze mysqlclient
RUN apt-get update && apt-get install -y gcc && apt-get install -y default-libmysqlclient-dev

#working directory
WORKDIR /app

#copy requirements file
COPY requirements.txt /app
#copy entire project structure
COPY ./main.py /app
COPY ./project /app/project

#install dependencies
RUN pip install -r requirements.txt

#flask gira sulla porta 5000
EXPOSE 5000

#avvio applicazione
CMD ["python", "main.py"]