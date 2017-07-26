import logging

import requests
from google import search

from .stackoverflow_parsing import find_answers

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
        for answer in find_answers(raw_html):
            yield answer
