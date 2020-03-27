import unittest
import os

from common.exceptions.parameters import InvalidParameterError, UnsupportedLanguageError
from common.mongo.controller import MongoController
from unittest.mock import Mock, patch
from bson import ObjectId

from mocks.mock_requests import MockResponse
from tasks import crawl_nyt_keyword

class TestTasks(unittest.TestCase):
    # Fixtures
    sample_user = 'sample user'
    sample_keyword_string = 'House'
    sample_keyword_language = 'en'

    sample_article = {
        '_id': 'nyt://article/84e7a531-986a-5293-b7a7-c343466738a0',
        'snippet': 'some snippet',
        'pub_date': '2020-03-03T17:43:00+0000',
    }

    def setUp(self):
        """
        Initialise the database
        """

        # Database
        self.mongo_controller = MongoController()
        self.sample_keyword = self.mongo_controller.add_keyword(self.sample_keyword_string, self.sample_keyword_language, self.sample_user, return_object=True,  cast=True)

    def tearDown(self):
        """
        Tear down the database
        """
        self.mongo_controller.client.drop_database(os.environ['MONGO_DATABASE_NAME'])

    @patch('requests.get')
    def test_crawl_nyt_keyword(self, requests_get_mock):
        """
        Test a keyword crawl and that it returned something
        """
        requests_get_mock.return_value = MockResponse(articles=[self.sample_article])
        result = crawl_nyt_keyword(self.sample_keyword.keyword_string, self.sample_keyword.language)
        self.assertTrue(result, 'Make sure the list is not empty')

    @patch('requests.get')
    def test_crawl_nyt_keyword_no_result(self, requests_get_mock):
        """
        Test a keyword crawl with no results returned
        """
        requests_get_mock.return_value = MockResponse(articles=[])
        result = crawl_nyt_keyword(self.sample_keyword.keyword_string, self.sample_keyword.language)
        self.assertFalse(result, 'Make sure the list is empty')

    @patch('requests.get')
    def test_crawl_nyt_keyword_content(self, requests_get_mock):
        """
        Test a keyword crawl and that it returned something
        """
        requests_get_mock.return_value = MockResponse(articles=[self.sample_article])
        result = crawl_nyt_keyword(self.sample_keyword.keyword_string, self.sample_keyword.language)
        self.assertTrue(result, 'Make sure the list is not empty')

        self.assertGreater(len(result), 0, 'Make sure at least one result was returned')
        result_target = result[0]
        
        self.assertIn('text', result_target, 'Make sure that the dict has an attribute called text')
        self.assertEqual(self.sample_article['snippet'], result_target['text'], 'Make sure the text matches')


    def test_crawl_nyt_keyword_invalid_keyword(self):
        """
        Test for invalid keyword inputs
        """
        self.assertRaises(InvalidParameterError, crawl_nyt_keyword, None, self.sample_keyword.language)

    def test_crawl_nyt_keyword_unsupported_language(self):
        """
        Test for invalid language inputs
        """
        self.assertRaises(UnsupportedLanguageError, crawl_nyt_keyword, self.sample_keyword.keyword_string, None)
