package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"path/filepath"
	"strconv"
	"strings"
)

// main folder FileServer
var uploadPath = "./Uploads"

// Exam struct to represent the post request of upload
type Exam struct {
	// file name
	StudentCode string
	// prof folder name
	ProfessorCode string
	// subject prof folder name
	Subject string
	// list of answers for all questions (string format)
	Answers string
	// list of answers for all questions (string format)
	Questions string
}

// Result struct to represent the post request of update file
type Result struct {
	// file name
	StudentCode string
	// prof folder name
	ProfessorCode string
	// subject prof folder name
	Subject string
	// result
	Result string
}

// Answer struct to represent student's answers to single question
type Answer struct {
	id_question int      `json:"id_question"`
	answers     []string `json:"answers"`
}

// Question struct to represent question
type Question struct {
	id_question     int      `json:"id_question"`
	text            string   `json:"text"`
	answers         []string `json:"answers"`
	correct_answers []string `json:"correct_answers"`
}

// Professor struct to represent the post request of delete
type Professor struct {
	code    string `json:"code"`
	subject string `json:"subject"`
}

func main() {
	// route handler upload
	http.HandleFunc("/upload", uploadFileHandler())

	// route handler write result on file
	http.HandleFunc("/update", resultFileHandler())

	// route handler delete files
	http.HandleFunc("/delete_exams", deleteFileHandler())

	// file server (download endpoint of static files)
	/*
		http.FileSystem is an interface defined in the net/http package.
		It represents an abstraction for reading files from a file system or any other datasource
		that can be accessed like a file system.
		Everything that has an Open method it can be used as instance of http.FileSystem
	*/
	fs := http.FileServer(http.Dir(filepath.Join(uploadPath, "/")))
	// route handler get file (every route that starts with /files is executed by the fs handler
	http.Handle("/files/", http.StripPrefix("/files", fs))

	/*
		difference between HandleFunc and Handle

		http.HandleFunc is a higher-level function that allows you to register a handler
		function for a specific URL pattern (route) directly.
		Internally, http.HandleFunc registers a HandlerFunc type that converts the provided
		function into a Handler interface,
		which is then registered with the default ServeMux multiplexer

		http.Handle is a lower-level function that allows you to register a handler object
		implementing the http.Handler interface for a specific URL pattern.
		The handler object you provide must have a ServeHTTP method with the signature
		ServeHTTP(http.ResponseWriter, *http.Request), which will be invoked to handle
		incoming HTTP requests.
	*/

	log.Print("Server started on 0.0.0.0:8080, use /upload for uploading files and /files/{fileName} for downloading")

	// start http server and if return error stop execution
	// the second parameter is the ServerMux (default in this case) --> is a router
	log.Fatal(http.ListenAndServe("0.0.0.0:8080", nil))
}

func uploadFileHandler() http.HandlerFunc {
	/*
		convert a function with the signature func(http.ResponseWriter, *http.Request)
		into a value of type http.Handler
		So we can use a user function as an HttpHandler and it creates
		a middleware with additional functionality
	*/
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// this function responds only on POST request
		if r.Method == "POST" {
			// read request body and cast to byte slice ([]byte)
			// require an object that implements io.Reader interface (datasource of data stream)
			body, err := io.ReadAll(r.Body)
			if err != nil {
				fmt.Println(err)
			}

			// retrieve post data
			var exam Exam
			err = json.Unmarshal(body, &exam)
			if err != nil {
				fmt.Println(err)
			}

			// initialize array of given answers
			var answers_struct []Answer
			// remove first char ([) and last char (])
			// now I have a sequence of strings (enclosed by {}) that represents single Answer object
			var tmp = strings.Split(exam.Answers[1:len(exam.Answers)], "}")
			for _, row := range tmp[:len(tmp)-1] {
				// the split method, when meet } return the first string without }
				// the second string starts with } and contains ,{ --> starts new Answer object
				// string representation
				if strings.Contains(row, ",{") {
					// remove },
					row = row[1:]
				}
				row += "}"

				/*
					from row remove {"id_question:
					split the new string on char , and get first result --> obtain id number
				*/
				var id = strings.Split(row[15:], ",")[0]

				/*
					from row remove {"id_question:
					from new string remove the length of id
					from new string remove the length of ,"answers":
					from new string remove the last char }
					from new string remove first and last char (remove [ and ])
				*/
				var answers = row[15+len(id)+11 : len(row)-1]
				answers = answers[1 : len(answers)-1]

				// from string to array of string
				var answers_list []string
				for _, element := range strings.Split(answers, " ") {
					answers_list = append(answers_list, element)
				}

				// from string to int
				id_question, err_conversion := strconv.Atoi(id)
				if err_conversion != nil {
					fmt.Println(err_conversion)
				}

				// create object and append to list
				var answer = Answer{id_question: id_question, answers: answers_list}
				answers_struct = append(answers_struct, answer)
			}

			// initialize array of submitted questions
			var questions_struct []Question
			// remove first char ([) and last two char (]) -->
			// now I have a sequence of strings (enclosed by {}) that represents single Question object
			tmp = strings.Split(exam.Questions[1:len(exam.Questions)], "}")
			for _, row := range tmp[:len(tmp)-1] {
				// the split method, when meet } return the first string without }
				// the second string starts with } and contains ,{ --> starts new Answer object
				// string representation
				if strings.Contains(row, ",{") {
					// remove },
					row = row[1:]
				}
				row += "}"

				/*
					from row remove {"id_question:
					split the new string on char , and get first result --> obtain id number
				*/
				var id = strings.Split(row[15:], ",")[0]

				/*
					from row remove {"id_question:
					from new string remove the length of id
					from new string remove the length of ,"text":
					split the new string on char , and get first result --> obtain text
				*/
				var text = strings.Split(row[15+len(id)+8:], ",")[0]

				/*
					from row remove {"id_question:
					from new string remove the length of id
					from new string remove the length of ,"text":
					from new string remove the length of text
					from new string remove the length of ,"answers":
					the new string is ["_","_","_"]
					split the new string on char ] (get end of list of response) and get first result --> obtain answers (add ] to close list)
				*/
				var answers = strings.Split(row[15+len(id)+8+len(text)+11:], "]")[0] + "]"

				/*
					from row remove {"id_question:
					from new string remove the length of id
					from new string remove the length of ,"text":
					from new string remove the length of text
					from new string remove the length of ,"answers":
					from new string remove the length of answers
					from new string remove the length of ,"correct_answers":
					from new string remove the last char }
					from new string remove first and last char (remove [ and ])
				*/
				var correct_answers = row[15+len(id)+8+len(text)+11+len(answers)+19 : len(row)-1]
				correct_answers = correct_answers[1 : len(correct_answers)-1]

				// from string to array of string
				var answers_list []string
				for _, element := range strings.Split(answers[1:len(answers)-1], " ") {
					answers_list = append(answers_list, element)
				}

				// from string to array of string
				var correcrt_answers_list []string
				for _, element := range strings.Split(correct_answers, " ") {
					correcrt_answers_list = append(correcrt_answers_list, element)
				}

				// from string to int
				id_question, err_conversion := strconv.Atoi(id)
				if err_conversion != nil {
					fmt.Println(err_conversion)
				}

				// create object and append to list
				var question = Question{id_question: id_question, answers: answers_list, correct_answers: correcrt_answers_list, text: text}
				questions_struct = append(questions_struct, question)
			}

			file_name := exam.StudentCode + ".csv"

			// ./Uploads/ProfCode/Subject/nome_file
			path := filepath.Join(filepath.Join(uploadPath, exam.ProfessorCode), exam.Subject)

			// check if directories exists
			_, err = os.Stat(path)

			if err != nil {
				if os.IsNotExist(err) {
					// creo le directory
					os.MkdirAll(path, os.ModePerm)
				} else {
					renderError(w, "CANT_CREATE_FOLDER", http.StatusInternalServerError)
					return
				}
			}

			// write file
			newFile, err := os.Create(filepath.Join(path, file_name))
			if err != nil {
				renderError(w, "CANT_WRITE_FILE", http.StatusInternalServerError)
				return
			}
			defer newFile.Close() // idempotent, okay to call twice

			wf := bufio.NewWriter(newFile)
			for _, question := range questions_struct {
				row := "Id Domanda: " + strconv.Itoa(question.id_question) + ";" +
					" Domanda: " + question.text + ";" +
					"Risposte: "
				for _, answer := range question.answers {
					row += answer + " "
				}
				row += "; Risposte corrette: "

				for _, answer := range question.correct_answers {
					row += answer + " "
				}
				row += "; Risposte date: "

				for _, answer := range answers_struct {
					if answer.id_question == question.id_question {
						for _, given_answer := range answer.answers {
							row += given_answer + " "
						}
					}
				}
				row += "\n"
				wf.WriteString(row)
				wf.Flush()
			}
			newFile.Close()
			w.Write([]byte(fmt.Sprintf("UPLOAD_SUCCESSFULLY")))
		}
	})
}

func resultFileHandler() http.HandlerFunc {
	/*
		convert a function with the signature func(http.ResponseWriter, *http.Request)
		into a value of type http.Handler
		So we can use a user function as an HttpHandler and it creates
		a middleware with additional functionality
	*/
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// this function responds only on POST request
		if r.Method == "POST" {
			// read request body and cast to byte slice ([]byte)
			// require an object that implements io.Reader interface (datasource of data stream)
			body, err := io.ReadAll(r.Body)
			if err != nil {
				fmt.Println(err)
			}

			// retrieve post data
			var result Result
			err = json.Unmarshal(body, &result)
			if err != nil {
				fmt.Println(err)
			}

			file_name := result.StudentCode + ".csv"

			// ./Uploads/ProfCode/Subject/nome_file
			path := filepath.Join(filepath.Join(uploadPath, result.ProfessorCode), result.Subject)

			// check if directories exists
			_, err = os.Stat(path)

			if err != nil {
				renderError(w, "Failed Upload", http.StatusInternalServerError)
				return
			}

			// write file
			file, err := os.OpenFile(filepath.Join(path, file_name), os.O_APPEND|os.O_WRONLY, 0644)
			if err != nil {
				renderError(w, "Failed upload", http.StatusInternalServerError)
			}
			_, err = file.WriteString(result.Result)

			file.Close()
			w.Write([]byte(fmt.Sprintf("WRITE_SUCCESSFULLY")))
		}
	})
}

func deleteFileHandler() http.HandlerFunc {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method == "POST" {
			body, err := io.ReadAll(r.Body)
			if err != nil {
				fmt.Println(err)
			}

			// retrieve post data
			var prof Professor
			err = json.Unmarshal(body, &prof)
			if err != nil {
				fmt.Println(err)
			}

			// ./Uploads/ProfCode/Subject/nome_file
			path := filepath.Join(filepath.Join(uploadPath, prof.code), prof.subject)

			// check if directories exists
			_, err = os.Stat(path)

			if err != nil {
				renderError(w, "Empty download section", http.StatusInternalServerError)
				return
			}

			// open dir - ./Uploads/ProfCode/Subjcet
			d, err := os.Open(filepath.Join(filepath.Join(uploadPath, prof.code), prof.subject))
			if err != nil {
				renderError(w, "PATH_MALFORMED", http.StatusInternalServerError)
				return
			}
			defer d.Close()

			// read dir content
			names, err := d.Readdirnames(-1)
			if len(names) == 0 {
				renderError(w, "Empty download section", http.StatusInternalServerError)
				return
			}
			if err != nil {
				renderError(w, "READ_ERROR", http.StatusInternalServerError)
				return
			}

			// iterate on files
			for _, name := range names {
				err = os.RemoveAll(filepath.Join(filepath.Join(filepath.Join(uploadPath, prof.code), prof.subject), name))
				if err != nil {
					renderError(w, "DELETING_ERROR", http.StatusInternalServerError)
					return
				}
			}
			w.Write([]byte(fmt.Sprintf("All exams in download deleted successfully")))
		}
	})
}

func renderError(w http.ResponseWriter, message string, statusCode int) {
	// write response header and body
	w.WriteHeader(statusCode)
	w.Write([]byte(message))
}
