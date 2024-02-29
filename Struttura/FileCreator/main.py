with open("student_file.csv", "w") as f:
    for i in range(0, 1000):
        f.write("{}; {}; matematica\n".format(i + 1, 1))

with open("student_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("{}; {}; italiano\n".format(i + 1, 2))

with open("student_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("{}; {}; inglese\n".format(i + 1, 3))

with open("question_file.csv", "w") as f:
    for i in range(0, 1000):
        f.write("1; matematica; Domanda {}; A; B; C; D; {}\n".format(i + 1, (i % 4) + 1))

with open("question_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("2; italiano; Domanda {}; A; B; C; D; {}\n".format(i + 1, (i % 4) + 1))

with open("question_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("3; inglese; Domanda {}; A; B; C; D; {}\n".format(i + 1, (i % 4) + 1))

with open("question_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("1; matematica; Domanda {}; A; B; C; D; {}\n".format(i + 1, [(i % 4) + 1, (((i % 4) + 2) % 4) + 1]))

with open("question_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("2; italiano; Domanda {}; A; B; C; D; {}\n".format(i + 1, [(i % 4) + 1, (((i % 4) + 2) % 4) + 1]))

with open("question_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("3; inglese; Domanda {}; A; B; C; D; {}\n".format(i + 1, [(i % 4) + 1, (((i % 4) + 2) % 4) + 1]))

with open("question_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("1; matematica; Domanda {}; E; F; C; D; {}\n".format(i + 1, (i % 4) + 1))

with open("question_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("2; italiano; Domanda {}; E; F; C; D; {}\n".format(i + 1, (i % 4) + 1))

with open("question_file.csv", "a") as f:
    for i in range(0, 1000):
        f.write("3; inglese; Domanda {}; E; F; C; D; {}\n".format(i + 1, (i % 4) + 1))

with open("realquestion_matematica_file.csv", "w") as f:
    for i in range(0, 5):
        f.write("1; matematica; Quanto fa 2 + 2 ; 4; 6; 8; -1; 1\n")

with open("realquestion_matematica_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("1; matematica; Quanto fa 3 / 3 ; 4; 6; 8; 1; 4\n")

with open("realquestion_matematica_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("1; matematica; Quanto fa 10 x 5 ; 45; 60; 50; 10; 3\n")

with open("realquestion_matematica_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("1; matematica; Qual e' la formula di Einstein ; E=mc^2; F=ma; E=c^2m; F=mg; [1, 3]\n")

with open("realquestion_italiano_file.csv", "w") as f:
    for i in range(0, 5):
        f.write("2; italiano; Chi ha scritto i promessi sposi; Manzoni; Dante; Petrarca; Foscolo; 1\n")

with open("realquestion_italiano_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("2; italiano; Chi ha scritto la divina commedia; Manzoni; Dante; Petrarca; Foscolo; 2\n")

with open("realquestion_italiano_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("2; italiano; Chi scrisse i sepolcri; Manzoni; Dante; Petrarca; Foscolo; 4\n")

with open("realquestion_italiano_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("2; italiano; Chi scrisse il decameron; Boccaccio; Dante; Giovanni Boccaccio; Foscolo; [1, 3]\n")


with open("realquestion_inglese_file.csv", "w") as f:
    for i in range(0, 5):
        f.write("3; inglese; The book is on the; table; cake; cat; dog; 1\n")

with open("realquestion_inglese_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("3; inglese; Please seat; down; up; left; right; 1\n")

with open("realquestion_inglese_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("3; inglese; Listen and ; repeat; see; touch; dance; 1\n")

with open("realquestion_inglese_file.csv", "a") as f:
    for i in range(0, 5):
        f.write("3; inglese; How writes the picture of dorian gray; Oscar Wilde; Shakespeare; Wilde; Swift; [1, 3]\n")