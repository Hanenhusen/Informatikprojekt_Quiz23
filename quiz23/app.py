from flask import Flask, render_template, request, redirect, url_for
from database import *

app = Flask(__name__)

# erstellte Tabellen in der Datenbank
createTables()

@app.route('/')
def home():
    """
    Rendert die Seite index.html.

    :return: gerendertes Template: index.html
    """
    return render_template("index.html")

@app.route('/index.html')
def index():
    """
    Rendert die Seite index.html.
    Alternative Route.

    :return: gerendertes Template: index.html
    """
    return render_template("index.html")

@app.route('/aboutProject.html')
def aboutProject():
    """
    Rendert die Seite aboutProject.html.

    :return: gerendertes Template: aboutProject.html
    """
    return render_template("aboutProject.html")

@app.route('/newQuiz.html', methods=['POST', 'GET'])
def createNewQuiz():
    """
    Verarbeitet das Erstellen eines neuen Quiz und rendert die Seite newQuiz.html.

    :return: gerendertes Template: newQuiz.html
    """
    if request.method == 'POST':
        try:
            dozent_id = request.form['dozent_id']
            thema = request.form['thema']

            # Erstelltes Quiz in Datenbank einfügen
            insertNewQuiz(dozent_id, thema)
            # Nach erfolgreicher Erstellung des Quiz zur Seite 'allQuizzes.html' umleiten
            return redirect(url_for('showAllQuizzes'))
        except:
            print("Error in the INSERT")
            return render_template("newQuiz.html")

    return render_template("newQuiz.html")


@app.route('/releaseQuiz/<int:quiz_id>', methods=['POST'])
def releaseQuiz(quiz_id):
    """
    Verarbeitet das Freigeben eines Quiz und aktualisiert den Freigabestatus in der Datenbank.

    :param quiz_id: Die ID des freizugebenden Quiz.
    :return: Weiterleitung zur Seite showAllQuizzes.
    """
    if request.method == 'POST':
        freigegeben = request.form.get('freigegeben') == 'on'

        # Freigabestatus in Datenbank aktualisieren
        updateReleaseStatus(freigegeben, quiz_id)

    return redirect(url_for('showAllQuizzes'))


@app.route('/allQuizzes.html')
def showAllQuizzes():
    """
    Rendert die Seite allQuizzes.html und zeigt alle vorhandenen Quizze in einer Tabelle an.

    :return: gerendertes Template: allQuizzes.html
    """
    result = getAllQuizzes()
    return render_template("allQuizzes.html", result=result)


def getQuizDataFromDatabase(quiz_id):
    """
    Holt die Quizdaten aus der Datenbank anhand der Quiz ID.

    :param quiz_id: Die ID des abzurufenden Quiz.
    :return: Die Daten des abgefragten Quiz als Dictionary.
    """
    quiz_data = fetchQuizDataFromDatabase(quiz_id)
    return quiz_data


def getQuestionsForQuiz(quiz_id):
    """
    Holt die Fragen für ein bestimmtes Quiz aus der Datenbank.

    :param quiz_id: Die ID des Quiz, für das die Fragen abgerufen werden sollen.
    :return: Eine Liste von Fragen als Dictionary.
    """
    questions_from_db = fetchQuestionsForQuiz(quiz_id)
    questions = []

    for question_row in questions_from_db:
        question = {
            "frage_id": question_row["frage_id"],
            "fragetyp": question_row["fragetyp"],
            "frage_inhalt": question_row["frage_inhalt"],
            "quiz_id": question_row["quiz_id"],
            "answers": fetchAnswersForQuestion(question_row["frage_id"])
        }
        questions.append(question)

    return questions

@app.route('/createNewQuestion/<int:quiz_id>', methods=['POST', 'GET'])
def createNewQuestion(quiz_id):
    """
    Verarbeitet das Erstellen einer neuen Frage für ein bestimmtes Quiz und rendert die Seite newQuestion.html.

    :param quiz_id: Die ID des Quiz, für das die Frage erstellt wird.
    :return: gerendertes Template: newQuestion.html
    """
    if request.method == 'POST':
        fragetyp = request.form['fragetyp']
        frage_inhalt = request.form['frage_inhalt']

        antwort_1 = request.form['antwort_1']
        antwort_2 = request.form['antwort_2']
        antwort_3 = request.form['antwort_3']
        antwort_4 = request.form['antwort_4']

        # wenn checkbox ausgewählt wurde
        ist_korrekt_1 = request.form.get('ist_korrekt_1') == 'on'
        ist_korrekt_2 = request.form.get('ist_korrekt_2') == 'on'
        ist_korrekt_3 = request.form.get('ist_korrekt_3') == 'on'
        ist_korrekt_4 = request.form.get('ist_korrekt_4') == 'on'

        # Frage in Datenbank einfügen und frage_id abrufen
        frage_id = insertNewQuestion(fragetyp, frage_inhalt, quiz_id)

        # Antworten in Datenbank einfügen
        insertNewAnswer(antwort_1, ist_korrekt_1, frage_id)
        insertNewAnswer(antwort_2, ist_korrekt_2, frage_id)
        insertNewAnswer(antwort_3, ist_korrekt_3, frage_id)
        insertNewAnswer(antwort_4, ist_korrekt_4, frage_id)

        # Nach dem Hinzufügen zu quiz.html umleiten
        return redirect(url_for('quiz', quiz_id=quiz_id))

    return render_template("newQuestion.html", quiz_id=quiz_id)


def getQuestionDataFromDatabase(frage_id):
    """
    Holt die Daten einer Frage aus der Datenbank anhand der Frage-ID.

    :param frage_id: Die ID der abzurufenden Frage.
    :return: Die Daten der abgefragten Frage als Dictionary.
    """
    question_data = fetchQuestionDataFromDatabase(frage_id)
    return question_data

def getAnswerDataFromDatabase(frage_id):
    """
    Holt die Antwortdaten einer Frage aus der Datenbank anhand der Frage-ID.

    :param frage_id: Die ID der Frage, für die die Antworten abgerufen werden sollen.
    :return: Die Antwortdaten der abgefragten Frage als Liste von Dictionaries.
    """
    answer_data = fetchAnswersForQuestion(frage_id)
    return answer_data

@app.route('/newQuestion.html/<int:quiz_id>')
def new_question(quiz_id):
    """
    Rendert die Seite newQuestion.html für das Erstellen einer neuen Frage für ein bestimmtes Quiz.

    :param quiz_id: Die ID des Quiz, für das die Frage erstellt wird.
    :return: gerendertes Template: newQuestion.html
    """
    return render_template("newQuestion.html", quiz_id=quiz_id)


@app.route('/quiz/<int:quiz_id>')
def quiz(quiz_id):
    """
    Rendert die Seite quiz.html für ein bestimmtes Quiz.

    :param quiz_id: Die ID des abzurufenden Quiz.
    :return: gerendertes Template: quiz.html oder error.html, falls das Quiz nicht gefunden wurde.
    """
    quiz_data = getQuizDataFromDatabase(quiz_id)
    questions = getQuestionsForQuiz(quiz_id)

    if quiz_data:
        return render_template('quiz.html', quiz_data=quiz_data, questions=questions)
    else:
        return render_template('error.html', message='Quiz nicht gefunden')


@app.route('/editQuiz/<int:quiz_id>', methods=['GET', 'POST'])
def editQuiz(quiz_id):
    """
    Verarbeitet das Bearbeiten eines Quiz und rendert die Seite editQuiz.html.

    :param quiz_id: Die ID des zu bearbeitenden Quiz.
    :return: Weiterleitung zur Seite showAllQuizzes oder error.html, falls das Quiz nicht gefunden wurde.
    """
    if request.method == 'POST':
        new_thema = request.form['new_thema']
        updateQuiz(new_thema, quiz_id)

        return redirect(url_for('showAllQuizzes'))

    quiz_data = getQuizDataFromDatabase(quiz_id)

    if quiz_data:
        return render_template('editQuiz.html', quiz_data=quiz_data)
    else:
        return render_template('error.html', message='Quiz nicht gefunden')


@app.route('/editQuestion/<int:frage_id>', methods=['GET', 'POST'])
def editQuestion(frage_id):
    """
    Verarbeitet das Bearbeiten einer Frage und rendert die Seite editQuestion.html.

    :param frage_id: Die ID der zu bearbeitenden Frage.
    :return: Weiterleitung zur Seite quiz oder error.html, falls die Frage nicht gefunden wurde.
    """
    question_data = fetchQuestionDataFromDatabase(frage_id)
    answer_data = fetchAnswersForQuestion(frage_id)

    if request.method == 'POST':
        new_frage_inhalt = request.form.get('frage_inhalt')
        new_fragetyp = request.form.get('fragetyp')

        updateQuestion(new_frage_inhalt, new_fragetyp, frage_id)

        for i in range(1, 5):
            new_antwort = request.form.get(f'antwort_{i}')
            new_ist_korrekt = request.form.get(f'ist_korrekt_{i}') == 'on'

            updateAnswer(new_antwort, new_ist_korrekt, answer_data[i - 1]['antwort_id'])

        return redirect(url_for('quiz', quiz_id=question_data['quiz_id']))

    return render_template('editQuestion.html', question_data=question_data, answer_data=answer_data)


@app.route('/deleteQuiz/<int:quiz_id>', methods=['GET', 'POST'])
def deleteQuizAll(quiz_id):
    """
    Verarbeitet das Löschen eines Quiz und rendert die Bestätigungsseite confirm_delete_quiz.html.

    :param quiz_id: Die ID des zu löschenden Quiz.
    :return: Weiterleitung zur Seite showAllQuizzes oder error.html, falls das Quiz nicht gefunden wurde.
    """
    if request.method == 'POST':
        # Lösche Quiz und zugehörige Daten aus der Datenbank
        deleteQuiz(quiz_id)
        # Optional: Lösche auch Fragen und Antworten, die mit dem Quiz verbunden sind

        # Nach dem Löschen zur allQuizzes-Seite umleiten
        return redirect(url_for('showAllQuizzes'))

    quiz_data = getQuizDataFromDatabase(quiz_id)

    if quiz_data:
        return render_template('confirm_delete_quiz.html', quiz_data=quiz_data)
    else:
        return render_template('error.html', message='Quiz nicht gefunden')


@app.route('/deleteQuestion/<int:frage_id>', methods=['GET', 'POST'])
def deleteQuestionAll(frage_id):
    """
    Verarbeitet das Löschen einer Frage und rendert die Bestätigungsseite confirm_delete_question.html.

    :param frage_id: Die ID der zu löschenden Frage.
    :return: Weiterleitung zur Seite showAllQuizzes oder error.html, falls die Frage nicht gefunden wurde.
    """
    if request.method == 'POST':
        deleteQuestion(frage_id)
        # Optional: Lösche auch Antworten, die mit der Frage verbunden sind

        # Nach dem Löschen zur allQuizzes-Seite umleiten
        return redirect(url_for('showAllQuizzes'))

    question_data = getQuestionDataFromDatabase(frage_id)

    if question_data:
        return render_template('confirm_delete_question.html', question_data=question_data)
    else:
        return render_template('error.html', message='Frage nicht gefunden')


@app.route('/playQuizzes.html')
def playQuizzes():
    """
    Rendert die Seite playQuizzes.html und zeigt eine Liste aller verfügbaren Quiz an.

    :return: gerendertes Template: playQuizzes.html
    """
    result = getAllQuizzes()
    return render_template("playQuizzes.html", result=result)


@app.route('/startQuiz/<int:quiz_id>', methods=['GET'])
def startQuiz(quiz_id):
    """
    Rendert die Seite startQuiz.html für den Beginn eines bestimmten Quiz.

    :param quiz_id: Die ID des zu startenden Quiz.
    :return: gerendertes Template: startQuiz.html oder error.html, falls das Quiz nicht gefunden wurde.
    """
    quiz_data = getQuizDataFromDatabase(quiz_id)
    questions = getQuestionsForQuiz(quiz_id)

    if quiz_data:
        return render_template('startQuiz.html', quiz_data=quiz_data, questions=questions)
    else:
        return render_template('error.html', message='Quiz nicht gefunden')


@app.route('/submitQuiz/<int:quiz_id>', methods=['POST'])
def submitQuiz(quiz_id):
    """
    Verarbeitet die eingereichten Antworten eines Benutzers für ein Quiz und rendert die Seite quizCompleted.html.

    :param quiz_id: Die ID des abgegebenen Quiz.
    :return: gerendertes Template: quizCompleted.html
    """
    if request.method == 'POST':

        # Feedback vom Formular abrufen
        feedback_text = request.form.get('feedback_text')
        # Feedback in die Datenbank einfügen
        insertFeedback(quiz_id, feedback_text)

        # Liste mit Benutzer-Antworten
        user_answers = {}

        # Formulardaten durchlaufen und Benutzerantworten sammeln
        for key, value in request.form.items():

            if key.startswith('answer_'):
                # Frage-ID und die ausgewählte Antwort-ID
                question_id = int(key.split('_')[1])
                answer_id = int(value)

                # Überprüfen, ob es sich um eine Multiple-Choice-Frage handelt
                is_multiple_choice = isMultipleChoiceQuestion(question_id)

                # Fallunterscheidung zwischen Single-Choice und Multiple-Choice
                if is_multiple_choice:
                    # Wenn die Frage eine Multiple-Choice-Frage ist, füge die Antwort-ID zur Liste hinzu
                    if question_id in user_answers:
                        user_answers[question_id].append(answer_id)
                    else:
                        user_answers[question_id] = [answer_id]
                else:
                    # Wenn die Frage eine Single-Choice-Frage ist, speichere die Antwort-ID in einer Liste
                    user_answers[question_id] = [answer_id]

        # evaluateQuiz-Funktion aufrufen, um die Anzahl der richtig beantworteten Fragen zu erhalten
        correct_answers_count, question_results = evaluateQuiz(quiz_id, user_answers)

        for result in question_results:
            frage_id = result['frage_id']
            # Hinzufügen der vollständigen Frage und Antworten zum question_results-Dict
            result['question_data'] = getQuestionDataFromDatabase(frage_id)
            result['answer_data'] = getAnswerDataFromDatabase(frage_id)

            # Hinzufügen der vom Benutzer ausgewählten Antwort zur Frage
            result['user_answer'] = user_answers.get(frage_id, [])

        return render_template('quizCompleted.html', correct_answers_count=correct_answers_count, question_results=question_results)


def evaluateQuiz(quiz_id, user_answers):
    """
    Bewertet das Quiz und gibt die Anzahl der richtig beantworteten Fragen zurück.

    :param quiz_id: Die ID des Quiz, das bewertet werden soll.
    :param user_answers: Ein Dictionary, das die vom Benutzer ausgewählten Antworten für jede Frage enthält.
    :return: Die Anzahl der richtig beantworteten Fragen und eine Liste der Ergebnisse pro Frage.
    """
    # Alle Fragen für das angegebene Quiz aus der Datenbank holen
    questions = getQuestionsForQuiz(quiz_id)

    # Zähler für die richtig beantworteten Fragen initialisieren
    correct_answers_count = 0

    # Liste für die Ergebnisse pro Frage
    question_results = []

    # Für jede Frage durchlaufen und die Benutzerantworten mit den richtigen Antworten vergleichen
    for question in questions:
        # Je nach Fragetyp die richtige Funktion aufrufen
        if question['fragetyp'] == 'single-choice':
            is_correct = evaluateSingleChoice(question, user_answers)
        elif question['fragetyp'] == 'multiple-choice':
            is_correct = evaluateMultipleChoice(question, user_answers)
        else:
            # Handle unbekannten Fragetyp hier
            is_correct = False

        if is_correct:
            correct_answers_count += 1
            question_result = {'frage_id': question['frage_id'], 'correct': True}
        else:
            question_result = {'frage_id': question['frage_id'], 'correct': False}

        question_results.append(question_result)

    # Rückgabe der Anzahl der richtig beantworteten Fragen und der Ergebnisse pro Frage
    return correct_answers_count, question_results


def evaluateSingleChoice(question, user_answers):
    """
    Bewertet die Benutzerantwort für eine Single Choice Frage.

    :param question: Die Frage, die bewertet werden soll.
    :param user_answers: Ein Dictionary, das die vom Benutzer ausgewählten Antworten für jede Frage enthält.
    :return: True, wenn die Antwort korrekt ist, andernfalls False.
    """
    # Bewertung von Single Choice Fragen
    correct_answer_id = [answer['antwort_id'] for answer in question['answers'] if answer['ist_korrekt']][0]

    # Holen der Benutzerantworten als Liste oder eine leere Liste, wenn die Antwort nicht ausgewählt wurde
    user_answer_ids = user_answers.get(question['frage_id'], [])

    # Überprüfen, ob die korrekte Antwort in den Benutzerantworten enthalten ist
    return correct_answer_id in user_answer_ids

def evaluateMultipleChoice(question, user_answers):
    """
    Bewertet die Benutzerantwort für eine Multiple Choice Frage.

    :param question: Die Frage, die bewertet werden soll.
    :param user_answers: Ein Dictionary, das die vom Benutzer ausgewählten Antworten für jede Frage enthält.
    :return: True, wenn die Antworten korrekt sind, andernfalls False.
    """
    # Bewertung von Multiple-Choice-Fragen
    correct_answer_ids = [answer['antwort_id'] for answer in question['answers'] if answer['ist_korrekt']]

    # Sicherstellen, dass user_answer_ids eine Liste ist
    user_answer_ids = user_answers.get(question['frage_id'], [])
    if not isinstance(user_answer_ids, list):
        user_answer_ids = [user_answer_ids]

    user_answer_ids = set(user_answer_ids)
    return set(user_answer_ids) == set(correct_answer_ids)

@app.route('/showFeedback/<int:quiz_id>')
def showFeedback(quiz_id):
    """
    Rendert die Seite showFeedback.html und zeigt das Feedback für ein bestimmtes Quiz an.

    :param quiz_id: Die ID des Quizzes, für das das Feedback angezeigt werden soll.
    :return: gerendertes Template: showFeedback.html
    """
    quiz_data = getQuizDataFromDatabase(quiz_id)
    feedback = fetchFeedbackForQuiz(quiz_id)

    return render_template('showFeedback.html', quiz_data=quiz_data, feedback=feedback)


if __name__ == "__main__":
    # startet den Flask-Entwicklungsserver im Debug-Modus auf dem Port 5000
    app.run(debug=True, port=5000)