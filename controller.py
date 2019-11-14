"""
Module to hanlde different scripts that the crawler can execute
"""

from crawler import NytCrawler

class Controller():
    """
    Hanldes the different scripts and order of execution
    """
    def __init__(self):
        """
        Initialise the crawler
        """
        self.crawler = NytCrawler()
