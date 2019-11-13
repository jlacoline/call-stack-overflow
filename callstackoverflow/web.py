import logging

import requests
from googlesearch import search

logger = logging.getLogger(__name__)


def fetch_stackoverflow_html(query):
    # search on google
    google_query = "site:stackoverflow.com python {}".format(query)
    logger.info('Querying google with "%s"', google_query)
    links = search(google_query, stop=3)

    # get html from stackoverflow and parse it
    for link in links:
        logger.info("Parsing stackoverflow answers at %s", link)
        raw_html = requests.get(link).text
        yield raw_html
