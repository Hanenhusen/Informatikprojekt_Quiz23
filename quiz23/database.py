import sqlite3

def connectDatabase():
    conn = sqlite3.connect('database.db')
    # print("verbunden mit Datenbank erfolgreich")
    return conn


def createTables():
    conn = connectDatabase()

    query_for_quiz_table = '''CREATE TABLE IF NOT EXISTS quiz (
    	quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
    	dozent_id int,
    	thema varchar(20),   
    	freigegeben boolean DEFAULT 0,  --New Attribute for release status
    	FOREIGN KEY (dozent_id) REFERENCES dozent (dozent_id)
    )'''
    conn.execute(query_for_quiz_table)

    query_for_student_table = '''CREATE TABLE IF NOT EXISTS student (
    	student_id int Not Null PRIMARY KEY,
    	matrikelnummer int,
    	student_name varchar(50),
    	studiengang varchar(30)
    )'''
    conn.execute(query_for_student_table)

    query_for_dozent_table = '''CREATE TABLE IF NOT EXISTS dozent (
    	dozent_id int Not Null PRIMARY KEY,
    	fachgebiet varchar(20),
    	dozent_name varchar(50)
    )'''
    conn.execute(query_for_dozent_table)

    query_for_frage_table = '''CREATE TABLE IF NOT EXISTS frage (
    	frage_id INTEGER PRIMARY KEY AUTOINCREMENT,
    	fragetyp varchar(20) Not Null CHECK (fragetyp='single-choice' OR fragetyp='multiple-choice'),
    	frage_inhalt text,
    	quiz_id int Not Null,
    	FOREIGN KEY (quiz_id) REFERENCES quiz (quiz_id)
    )'''
    conn.execute(query_for_frage_table)

    query_for_antwort_table = '''CREATE TABLE IF NOT EXISTS antwort (
    	antwort_id INTEGER PRIMARY KEY AUTOINCREMENT,
    	antwort_inhalt text,
    	ist_korrekt boolean,
    	frage_id int Not Null,
    	FOREIGN KEY (frage_id) REFERENCES frage (frage_id)
    )'''
    conn.execute(query_for_antwort_table)

    query_for_feedback_table = '''CREATE TABLE IF NOT EXISTS feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id int Not Null,
        feedback_text text,
        FOREIGN KEY (quiz_id) REFERENCES quiz (quiz_id)
    )'''
    conn.execute(query_for_feedback_table)

    query_for_student_quiz_table = '''CREATE TABLE IF NOT EXISTS student_quiz (
        student_id int Not Null,
        quiz_id int Not Null,
        punktestand int,
        PRIMARY KEY (student_id, quiz_id),
        FOREIGN KEY (quiz_id) REFERENCES quiz (quiz_id),
        FOREIGN KEY (student_id) REFERENCES student (student_id)
    )'''
    conn.execute(query_for_student_quiz_table)
    # print('ALLE TABELLEN WURDEN ERFOLGREICH ERSTELLT!')
    conn.close()


def insertFeedback(quiz_id, feedback_text):
    # Überprüft das feedback_text, ob der nicht leer ist
    if feedback_text is not None and feedback_text.strip() != "":
        conn = connectDatabase()
        cur = conn.cursor()
        cur.execute("INSERT INTO feedback (quiz_id, feedback_text) VALUES (?, ?)",
                    (quiz_id, feedback_text))
        conn.commit()
        conn.close()
    else:
        print("Feedbacktext ist leer und wird nicht gespeichert.")


def insertNewQuiz(dozent_id, thema):
    # Verbindung mit der SQLite3-Datenbank
    conn = connectDatabase()
    cur = conn.cursor()
    # Ein neues Quiz hinzugefügt
    cur.execute("INSERT INTO quiz (dozent_id, thema) VALUES (?,?)", (dozent_id, thema))
    # In der Datenbank gespeichert
    conn.commit()
    # print("A new Quiz successfully added to database")
    # schließt die Verbindung
    conn.close()


def updateReleaseStatus(freigegeben, quiz_id):
    conn = connectDatabase()
    cur = conn.cursor()

    # Aktualisierung des Release-Status (Freigabestatus) im Quiz Tabelle
    cur.execute("UPDATE quiz SET freigegeben = ? WHERE quiz_id = ?", (freigegeben, quiz_id))

    conn.commit()
    # print(f"Updated the release status for Quiz ID {quiz_id}.")
    conn.close()


def getAllQuizzes(include_unreleased=True):
    # Verbindung mit der SQLite3-Datenbank
    conn = connectDatabase()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if include_unreleased:
        # alle Zeilen aus der Quiz-Tabelle ausgewählt
        cur.execute("SELECT * FROM quiz")
    else:
        # nur die freigegebenen Quizze ausgewählt
        cur.execute("SELECT * FROM quiz WHERE freigegeben = 1")

    # Holt alle Zeilen (Quiz) aus der Quiz-Tabelle.
    allQuizzes = cur.fetchall()
    conn.close()
    return allQuizzes


def fetchQuizDataFromDatabase(quiz_id):
    conn = connectDatabase()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT * FROM quiz WHERE quiz_id = ?", (quiz_id,))

    quiz_data = cur.fetchone()
    conn.close()

    return quiz_data


def updateQuiz(new_thema, quiz_id):
    conn = connectDatabase()
    cur = conn.cursor()
    # aktualisiert Quiz mit neuem Thema
    cur.execute("UPDATE quiz SET thema = ? WHERE quiz_id = ?", (new_thema, quiz_id))
    # In der Datenbank gespeichert
    conn.commit()
    # print("Thema erfolgreich aktualisiert")
    conn.close()


def updateQuestion(new_frage_inhalt, new_fragetyp, frage_id):
    conn = connectDatabase()
    cur = conn.cursor()
    # Frage mit neuem Frageinhalt und neuem Fragetyp aktualisiert
    cur.execute("UPDATE frage SET frage_inhalt = ?, fragetyp= ? WHERE frage_id = ?", (new_frage_inhalt,new_fragetyp, frage_id))

    # In der Datenbank gespeichert
    conn.commit()
    # print("Frage erfolgreich aktualisiert")
    conn.close()


def deleteQuiz(quiz_id):
    conn = connectDatabase()
    cur = conn.cursor()

    # Quiz mit der angegebenen quiz_id löschen
    cur.execute("DELETE FROM quiz WHERE quiz_id = ?", (quiz_id,))

    # Lösche zugehörige Fragen und Antworten
    cur.execute("DELETE FROM frage WHERE quiz_id = ?", (quiz_id,))

    conn.commit()

    conn.close()


def insertNewQuestion(fragetyp, frage_inhalt, quiz_id):
    conn = connectDatabase()
    cur = conn.cursor()
    cur.execute("INSERT INTO frage (fragetyp, frage_inhalt, quiz_id) VALUES (?,?,?)",
                (fragetyp, frage_inhalt, quiz_id))
    conn.commit()

    # Ruft die ID der zuletzt eingefügten Frage ab
    cur.execute("SELECT last_insert_rowid()")
    frage_id = cur.fetchone()[0]

    # print("Eine neue Frage wurde erfolgreich zur Datenbank hinzugefügt")
    conn.close()

    return frage_id


def fetchQuestionsForQuiz(quiz_id):
    conn = connectDatabase()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT * FROM frage WHERE quiz_id = ?", (quiz_id,))

    questions = cur.fetchall()

    conn.close()

    return questions


def fetchQuestionDataFromDatabase(frage_id):
    conn = connectDatabase()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT * FROM frage WHERE frage_id = ?", (frage_id,))

    question_data = cur.fetchone()
    conn.close()

    return question_data


def deleteQuestion(frage_id):
    conn = connectDatabase()
    cur = conn.cursor()

    # Frage mit der angegebenen frage_id löschen
    cur.execute("DELETE FROM frage WHERE frage_id = ?", (frage_id,))

    # Verknüpfte Antworten löschen
    cur.execute("DELETE FROM antwort WHERE frage_id = ?", (frage_id,))

    conn.commit()
    # print(f"Frage mit ID {frage_id} und zugehörige Antworten erfolgreich gelöscht. ")
    conn.close()


def insertNewAnswer (antwort_inhalt, ist_korrekt, frage_id):
    conn = connectDatabase()
    cur = conn.cursor()
    cur.execute("INSERT INTO antwort (antwort_inhalt, ist_korrekt, frage_id) VALUES (?,?,?)",
                        (antwort_inhalt, ist_korrekt, frage_id))

    cur.execute("SELECT last_insert_rowid()")
    antwort_id = cur.fetchone()[0]
    conn.commit()

    conn.close()

    return antwort_id

def updateAnswer(antwort_inhalt, ist_korrekt, antwort_id):
    conn = connectDatabase()
    cur = conn.cursor()

    cur.execute("UPDATE antwort SET antwort_inhalt = ?, ist_korrekt = ? WHERE antwort_id = ?",
                (antwort_inhalt, ist_korrekt, antwort_id))

    conn.commit()
    # print(f"Antwort mit ID {antwort_id} erfolgreich aktualisiert. ")
    conn.close()

def fetchAnswersForQuestion(frage_id):
    conn = connectDatabase()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT * FROM antwort WHERE frage_id = ?", (frage_id,))

    answers = cur.fetchall()
    conn.close()

    return answers

def isMultipleChoiceQuestion(question_id):
    conn = connectDatabase()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT fragetyp FROM frage WHERE frage_id = ?", (question_id,))

    fragetyp = cur.fetchone()

    conn.close()

    # Überprüft, ob die Frage existiert und der Fragetyp "multiple-choice" ist
    return fragetyp is not None and fragetyp['fragetyp'] == 'multiple-choice'

def fetchFeedbackForQuiz(quiz_id):
    conn = connectDatabase()
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()
    cur.execute("SELECT * FROM feedback WHERE quiz_id = ?", (quiz_id,))

    feedback = cur.fetchall()
    conn.close()

    return feedback

def deleteFeedbackForQuiz(quiz_id):
    conn = connectDatabase()
    cur = conn.cursor()

    cur.execute("DELETE FROM feedback WHERE quiz_id = ?", (quiz_id,))

    conn.commit()
    # print(f "Feedback zum Quiz mit ID {quiz_id} wurde erfolgreich gelöscht. ")
    conn.close()
