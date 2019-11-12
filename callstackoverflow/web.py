import logging
import re

import requests
from googlesearch import search

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def fetch_stackoverflow_answers(query):
    # search on google
    google_query = "site:stackoverflow.com python {}".format(query)
    logger.info('Querying google with "%s"', google_query)
    links = search(google_query, stop=1)

    # get html from stackoverflow and parse it
    for link in links:
        logger.info("Parsing stackoverflow answers at %s", link)
        raw_html = requests.get(link).text
        soup = BeautifulSoup(raw_html, 'html.parser') # TODO try except
        answers = soup.find_all("div", id=re.compile(r"answer-.*"))
        for answer in answers:
            yield str(answer)
