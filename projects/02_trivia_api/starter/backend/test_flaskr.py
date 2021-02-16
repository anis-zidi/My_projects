import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'answer': 'France',
            'category': '6',
            'difficulty': 4,
            'question': 'Who won the last world cup?'
        }

        
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO # DONE
    Write at least one test for each test for successful operation and for expected errors.
    """

    #-------------------------------ENDPOINTS----------------------------------

    #This test is for getting the categories                              #DONE
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    #This test is for getting paginated questions                         #DONE
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    #This test is for deleting a question                                 #DONE
    def test_delete_questions(self):
        #We will create a question that will be deleted in the test 
        create_question = {
            'question' : 'This is a test question?',
            'answer' : 'This a test answer',
            'category' : '1',
            'difficulty' : 1
        } 
        res = self.client().post('/questions', json = create_question)
        data = json.loads(res.data)
        question_id = data['question_new']

        #Now we will execute the test for deleting the 'create_question'
        res = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question_id))
        
    #This test if for creating a new question                             #DONE
    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    #This test if for searching for a question                            #DONE
    def test_search_question(self):
        search_question = {'searchTerm' : 'actor'}
        
        res = self.client().post('/questions', json = search_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    #This test is for getting questions by category                       #DONE
    def test_get_questions_by_category(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    #This test is for playing the quiz
    def test_play_the_quizz(self):
        new_quizz = {'previous_questions': [],
                    'quiz_category': {'type': 'Sports', 'id': 6}}
        
        res = self.client().post('/quizzes', json=new_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

#----------------------------------ERROR-HANDLERS--------------------------------

    #This test if for the error handler 404 : none found requests         #DONE
    def test_404_if_question_does_not_exist(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    #This test is for the error handler 422                               #DONE
    def test_422_unprocessable_request(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()