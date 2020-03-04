"""
Module to hanlde different scripts that the crawler can execute
"""
from common.mongo.controller import MongoController
from common.utils.logging import DEFAULT_LOGGER, LogTypes
from common.celery import queues

from crawler import NytCrawler
from tasks import app

class Controller():
    """
    Hanldes the different scripts and order of execution
    """
    def __init__(self):
        """
        Initialise the crawler
        """
        self.crawler = NytCrawler()
        self.mongo_controller = MongoController()

    def __save_nyt_result(self, nyt_article):
        """
        Save a nyt article to the MongoDb

        :param dict nyt_article: The result received packaged up
        """
        if nyt_article:
            crawl = self.mongo_controller.add_crawl_nyt(
                nyt_article['keyword_id'],
                nyt_article['article_id'],
                nyt_article['text'],
                nyt_article['timestamp'],
                return_object=True,
                cast=True
            )

            DEFAULT_LOGGER.log(f'Stored crawl result {crawl.to_json()}', log_type=LogTypes.INFO.value)

            app.send_task('process-crawl', kwargs={ 'crawl_dict': crawl.to_json() }, queue=queues['processor'])

            return crawl

    def __save_nyt_results(self, nyt_articles):
        """
        Save all nyt articles

        :param list<dict> nyt_articles: The to be saved nyt articles
        """
        crawls = [self.__save_nyt_result(article) for article in nyt_articles]
        return crawls

    def run_single_keyword(self, keyword_string, language):
        """
        Crawl a single keyword

        :param str keyword_string: Target keyword string
        :param str language: Target language
        """
        keyword = self.mongo_controller.get_keyword(keyword_string, language, cast=True)
        nyt_articles = self.crawler.get_articles(keyword)
        return self.__save_nyt_results(nyt_articles)
