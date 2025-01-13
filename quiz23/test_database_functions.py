import unittest
from database import *

class MyTestCase(unittest.TestCase):

    def test_insertNewQuizDeleteQuizGetAllQuizzes(self):
       # Einfügen eines neuen Testquizs
       insertNewQuiz(11, "Test Thema 1")
       # Alle Quizze aus der Datenbank abrufen
       test_quizzes = getAllQuizzes()
       # Überprüfen
       self.assertEqual(test_quizzes[-1]['thema'], "Test Thema 1")
       # Gibt es/Existiert ein Quiz, dessen Thema "Test Thema 1" ist?
       self.assertTrue(any(quiz["thema"] == "Test Thema 1" for quiz in test_quizzes))

       test_quiz_data = test_quizzes[-1]
       deleteQuiz(test_quiz_data["quiz_id"])
       test_quizzes = getAllQuizzes()
       self.assertFalse(any(quiz["thema"] == "Test Thema 1" for quiz in test_quizzes))


    def test_fetchQuizDataFromDatabase(self):
       insertNewQuiz(22, "Test Thema 2")
       test_quizzes = getAllQuizzes()
       test_quiz_data = test_quizzes[-1]
       test_quiz_data_id = test_quiz_data['quiz_id']
       test_quiz_data_fetched = fetchQuizDataFromDatabase(test_quiz_data_id)
       self.assertEqual(test_quiz_data_id, test_quiz_data_fetched['quiz_id'])
       deleteQuiz(test_quiz_data_id)


    def test_updateQuiz(self):
       insertNewQuiz(33, 'Test Thema 3')
       quiz_id = getAllQuizzes()[-1]['quiz_id']
       updateQuiz('Updated Test Thema', quiz_id)
       updated_quiz_data = fetchQuizDataFromDatabase(quiz_id)
       self.assertEqual(updated_quiz_data['thema'], 'Updated Test Thema')
       deleteQuiz(quiz_id)

    def test_UpdateReleaseStatus(self):
       insertNewQuiz(77, 'Test Thema 7')
       quiz_id = getAllQuizzes()[-1]['quiz_id']
       quiz_data = fetchQuizDataFromDatabase(quiz_id)
       quiz_data_freigegeben = quiz_data["freigegeben"]
       self.assertFalse(quiz_data_freigegeben)
       self.assertEqual(quiz_data_freigegeben, 0)
       deleteQuiz(quiz_id)


    def test_insertNewQuestionFetchQuestionsForQuiz(self):
       insertNewQuiz(44, 'Test Thema 4')
       quiz_id = getAllQuizzes()[-1]['quiz_id']
       question_id = insertNewQuestion('single-choice', 'Test Question 1', quiz_id)

       # Fragen für das Quiz abrufen und prüfen, ob die neue Frage vorhanden ist
       questions = fetchQuestionsForQuiz(quiz_id)
       self.assertTrue(any(question['frage_id'] == question_id for question in questions))
       deleteQuiz(quiz_id)


    def test_insertNewAnswerFetchAnswersForQuestionDeleteQuestion(self):
       insertNewQuiz(55, 'Test Thema 5')
       quiz_id = getAllQuizzes()[-1]['quiz_id']
       question_id = insertNewQuestion('single-choice', 'Test Question 2', quiz_id)
       answer_id = insertNewAnswer('Test Answer 1', True, question_id)

       # Antworten für die Frage abrufen und prüfen, ob die neue Antwort vorhanden ist
       answers = fetchAnswersForQuestion(question_id)
       self.assertTrue(any(answer['antwort_id'] == answer_id for answer in answers))

       deleteQuestion(question_id)
       answers = fetchAnswersForQuestion(question_id)
       self.assertFalse(any(answer['antwort_id'] == answer_id for answer in answers))

       deleteQuiz(quiz_id)

    def test_FetchQuestionDataFromDatabase(self):
       insertNewQuiz(66, 'Test Thema 6')
       quiz_id = getAllQuizzes()[-1]['quiz_id']
       question_id = insertNewQuestion('single-choice', 'Test Question 3', quiz_id)

       # Frage aus der Datenbank holen und prüfen
       question = fetchQuestionDataFromDatabase(question_id)
       self.assertTrue(question['frage_id'] == question_id)
       self.assertEqual(question['frage_id'], question_id)
       deleteQuestion(question_id)
       deleteQuiz(quiz_id)

    def test_updateQuestion(self):
       insertNewQuiz(88, "Test Thema 8")
       quiz_id = getAllQuizzes()[-1]['quiz_id']
       question_id = insertNewQuestion('multiple-choice', 'Test Question 4', quiz_id)
       question = fetchQuestionDataFromDatabase(question_id);
       updateQuestion("Updated Question 4", "single-choice",question_id)
       questionUpdated = fetchQuestionDataFromDatabase(question_id)
       self.assertNotEqual(question['frage_inhalt'], questionUpdated['frage_inhalt'])
       self.assertEqual(questionUpdated['fragetyp'], "single-choice")
       deleteQuestion(question_id)
       deleteQuiz(quiz_id)

    def test_updateAnswer(self):
       insertNewQuiz(99, "Test Thema 9")
       quiz_id = getAllQuizzes()[-1]['quiz_id']
       question_id = insertNewQuestion('multiple-choice', 'Test Question 5', quiz_id)
       insertNewAnswer("Falsch", 0, question_id)
       answers = fetchAnswersForQuestion(question_id)
       antwort_id = answers[0]['antwort_id']

       # Test
       updateAnswer('Richtig', 1, antwort_id)

       # Assert
       answersUpdated = fetchAnswersForQuestion(question_id)
       self.assertEqual(answersUpdated[0]['antwort_inhalt'], 'Richtig')
       self.assertEqual(answersUpdated[0]['ist_korrekt'], 1)

       # Aufräumen
       deleteQuestion(question_id)
       deleteQuiz(quiz_id)

    def test_fetchFeedbackForQuiz(self):
       insertNewQuiz(111, "Test Thema Feedback")
       test_quizzes = getAllQuizzes()
       test_quiz_data = test_quizzes[-1]
       test_quiz_id = test_quiz_data['quiz_id']

       # Feedback für das quiz
       feedback_text = "Test Feedback for Quiz"
       insertFeedback(test_quiz_id, feedback_text)

       # Holt feedback für das quiz
       feedback = fetchFeedbackForQuiz(test_quiz_id)

       # Überprüft, ob das Feedback in den abgerufenen Ergebnissen vorhanden ist
       self.assertTrue(any(entry["feedback_text"] == feedback_text for entry in feedback))

       # Aufräumen
       deleteFeedbackForQuiz(test_quiz_id)
       deleteQuiz(test_quiz_id)


    def test_isMultipleChoiceQuestion(self):
       insertNewQuiz(222, "Test Thema Multiple Choice")
       test_quizzes = getAllQuizzes()
       test_quiz_data = test_quizzes[-1]
       test_quiz_id = test_quiz_data['quiz_id']

       # Eine neue multiple-choice Frage
       question_id = insertNewQuestion('multiple-choice', 'Test Multiple Choice Question', test_quiz_id)

       # Überprüft, ob die Frage als Multiple-Choice-Frage identifiziert ist
       is_multiple_choice = isMultipleChoiceQuestion(question_id)
       self.assertTrue(is_multiple_choice)

       # Löscht test Question und test Quiz
       deleteQuestion(question_id)
       deleteQuiz(test_quiz_id)


if __name__ == '__main__':
    unittest.main()