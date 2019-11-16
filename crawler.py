"""
This module provides functionality to connect to the New York Times API.
And retrieve articles from said API.
"""

import os
import sys
import math
import time
import requests

from common.utils.logging import DEFAULT_LOGGER, LogTypes

class NytCrawler():
    """
    This class in an interface to the New York Times API

    NYT only allows you to use their service for non commercial use
    if you want to use it commericially then you will have to contact them.
    https://developer.nytimes.com/faq#a9
    """
    def __init__(self):
        """
        Set up credentials
        """
        # Credentials
        self.api_key = os.environ['NYT_API_KEY']
        self.api_secret = os.environ['NYT_API_SECRET']

        # Basic URLs
        self.url_root = 'https://api.nytimes.com/svc/'
        self.url_article_search = 'search/v2/articlesearch.json?'

    def __send_continous(self, request, retries=0):
        """
        Send a request continuesly taking care of rate limits and different types of responses

        :param Func request: The request that shall be sent
        :param int retries: The amount of times the request was tried to send
        """
        ON_RATE_LIMIT_SLEEP_TIME = 10 # seconds
        RETRY_LIMIT = 10 # How often you should wait for rate limit on the same page

        if retries == RETRY_LIMIT: # When the retry limit was reached
            DEFAULT_LOGGER.log('Retry limit was reached, this might be a more serious issue, aborting...', LogTypes.ERROR.value)
            return False # Abort

        try:
            response = request() # Try sending the request
        except Exception as ex: # If an error accours
            DEFAULT_LOGGER.log('There was an error within the request class itself, this might be a more serious issue, aborting...', LogTypes.ERROR.value, ex)
            return False # Abort

        if 'fault' in response: # Rate limit was probably exceeded
            DEFAULT_LOGGER.log('Article search request got rejected because of "{}", sleeping for {} seconds and then retrying'.format(response['fault']['faultstring'], ON_RATE_LIMIT_SLEEP_TIME), LogTypes.INFO.value) # This is technically an error but one that will occur all the time -> Log-type Info
            time.sleep(ON_RATE_LIMIT_SLEEP_TIME) # Wait for x seconds
            return self.__send_continous(request, retries + 1) # Try again

        if response['status'] != 'OK': # If we stop getting valid results
            return False # Abort

        return response # Return the response if non of the above guards triggered

    def __send_article_search_request(self, query, page):
        """
        Send an article search request
        
        :param str query: The string used to find the articles
        :param int page: The current page we are on
        """
        url = (
            self.url_root +
            self.url_article_search +
            'q={}&'.format(query) + # Actual query
            'page={}&'.format(page) +
            'api-key={}'.format(self.api_key)
        )

        DEFAULT_LOGGER.log('Sending NYT article search request for keyword "{}" on page {}...'.format(query, page), LogTypes.INFO.value)
        response = self.__send_continous(lambda: requests.get(url).json()) # Send a continous request
        return response

    def __response_doc_to_nyt_dict(self, keyword_string, language, response_doc):
        """
        Casts an API response to a list of nyt result objects

        :param str keyword: The target keyword used for the request
        :param str language: The target language
        :param dict response_doc: The API response document
        """
        try: # Try to get the required information
            article_id = response_doc['_id'].split('/')[-1] # id format = nyt://article/84e7a531-986a-5293-b7a7-c343466738a0 and we just want the part after the last "/"
            text = response_doc['snippet']
        except: # The response doc doen't have the required information
            return None # Abort
        
        if text is not '': # If there is a snippet
            return { 
                'article_id': article_id, 
                'keyword_string': keyword_string, 
                'language': language, 
                'text': text 
            }
        else:
            return None # Abort

    def get_articles(self, keyword_string, language, limit=sys.maxsize):
        """
        Get articles from the NYT API

        :param str keyword: The target keyword used for the request
        :param str language: The target language
        :param int limit: The maximum amount of articles returned
        """
        articles_per_request = 10 # NYT returns 10 articles at a time
        page_limit = 200 # NYT allows you to go up to 200 and not further
        amount_requests = min(articles_per_request * page_limit, math.ceil( limit / articles_per_request)) # Get the max amount of articles or as many as requested

        articles = []
        for i in range(amount_requests):
            response = self.__send_article_search_request(keyword_string, i) # Send search article request

            if (not response): # If you didn't get a valid response
                break # Abort

            articles_current = response['response']['docs'] # Extract the articles from the response
            articles_casted = [self.__response_doc_to_nyt_dict(keyword_string, language, response_doc) for response_doc in articles_current] # Cast the dicts to Nyt Results
            articles += articles_casted # Add casted articles to the articles list

        return articles[:limit] # Articles come in chunks of 10 so make sure you cut off extra articles

