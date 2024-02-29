mysql -u root -p$MYSQL_ROOT_PASSWORD <<EOF

DROP DATABASE IF EXISTS $MYSQL_DATABASE;
CREATE DATABASE $MYSQL_DATABASE;
USE $MYSQL_DATABASE;

CREATE TABLE student(
  id int NOT NULL AUTO_INCREMENT,
  student_code varchar(255) NOT NULL,
  professor_code varchar(255) NOT NULL,
  subject varchar(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY code_subject (student_code, professor_code, subject)
);

CREATE TABLE professor(
  id int NOT NULL AUTO_INCREMENT,
  code varchar(255) NOT NULL,
  password varchar(255) NOT NULL,
  subject varchar(255) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY code_subject (code, subject)
);

exit
EOF