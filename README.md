# Progetto di Advanced Programming Language

## Cerruto - Traina

## Librerie utilizzate
### Python
#### Flask (framework web)
#### flask-mongoengine (connettore per MongoDb e Flask)
#### requests (api rest request)
#### redis (connettore per Redis)
#### matplotlib (rendering dei grafici)

### C#
#### Microsoft.Extensions.Hosting.Systemd (per consentire il deploy di c# dentro docker container)
#### Newtonsoft.Json (per consentire la gestione dei JSON)
#### ServiceStack.Redis (per consentire l'interfacciamo con i database Redis)
#### MySqlConnector (per consentire l'interfacciamento con i database MySQL)
#### Dapper versione (per consentire l'utilizzo dei comandi MySQL)

### Go
#### varie librerie di I/O (bufio, fmt, io)
#### encoding/json (consersione string a JSON e viceversa)
#### net/http (client e server http)
#### path/filepath (utility di formattazione path

## Istruzioni per il build del docker compose
**Richiede l'installazione di docker desktop**

Per effettuare il build del progetto basta utilizzare il file docker-compose.yaml:
avendo docker engine avviato, posizionarsi nella root directory del progetto e
digitare nel terminale il seguente comando:

**docker compose up**

In questo modo non solo verranno costruite (o recuperate da docker hub) le immagini dei micro servizi, ma la costruzione e l'avvio dei container avverrà rispettando una catena di dipendenza specificata nel file in questione (tramite healtcheck e condition sui service). Inoltre, verranno creati anche i volumi per le componenti stateful del progetto (i database) e le diverse reti in cui si collocano i micro servizi.

## Utilizzo
Per far funzionare correttamente l'applicazione, bisogna innanzitutto configurare il sistema.

### Inizializzazione
1) collegarsi al professorserver

**http://localhost:5002/**

2) effettuare register e successivamente login 

**! per utilizzare i file predisposti inserire nel campo **subject** va inserito matematica, italiano, inglese oppure spagnolo e nel campo **code** 1, 2, 3 o 4 (rispettivamente)**

3) caricare i file di studenti (pagina **Add Student**) e domande (pagina **Add Questions**)

4) parametrizzare il compito (pagina **Exam Parameters**)

Una volta configurato il sistema lo studente è abilitato all'utilizzo della piattaforma.

### Utilizzo da parte dello studente
1) collegarsi allo studentserver

**http://localhost:5001/**

2) effettuare il login

**! per poter continuare inserire nel campo **Student Code** un valore nel range [1, 1000] se si sceglie come subject matematica, italiano o inglese (inserire nel campo **Professor code** 1, 2 o 3 rispettivamente) oppure nel range [1001, 2000] se si sceglie come subject spagnolo (inserire nel campo **Professor code** 4)**

3) una volta autenticato viene automaticamente generato il compito e si può procedere con la sottomissione (una domanda per volta)

**le risposte vengono temporaneamente memorizzate su un database Redis**

4) una volta terminato il compito, questo viene corretto e memorizzato (sia come file sia come record del database Mongo predisposto)

**se lo studente riprova ad effettuare un nuovo compito la piattaforma automaticamente lo reindirizza nella pagina di riepilogo del compito**

### Recupero informazioni da parte del professore
In qualsiasi momento il professore può recuperare le metrice (pagina **Metrics**) e i file consegnati (pagina **Download**)

### Reset del sistema
In qualsiasi momento il professore può decidere di resettare il sistema (pagina **Restore**). Questa azione comporta l'eliminazione di 

1) domande,

2) studenti

3) file

4) metriche

**! il professorcontroller si occuperà di bloccare l'azione nel caso in cui ci siano ancora compiti non consegnati così da consentire la futura correzione**
