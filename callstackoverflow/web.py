import os
import logging
import base64

import requests
from googlesearch import search

from .stackoverflow_parsing import find_stackoverflow_answers

logger = logging.getLogger(__name__)

GITHUB_SEARCH_URL = "https://api.github.com/search/code"


class GithubAnswer:
    def __init__(self, code):
        self._code = code

    def code_blocks(self):
        yield self._code

    def doc_links(self):
        yield from ()  # empty


def fetch_stackoverflow_answers(query):
    # search on google
    google_query = "site:stackoverflow.com python {}".format(query)
    logger.info('Querying google with "%s"', google_query)
    links = search(google_query, stop=3)

    # get html from stackoverflow and parse it
    for link in links:
        logger.info("Parsing stackoverflow answers at %s", link)
        raw_html = requests.get(link).text
        for stackoverflow_answer in find_stackoverflow_answers(raw_html):
            yield stackoverflow_answer


def fetch_github_answers(query):
    try:
        creds = os.environ["GITHUB_CREDS"]
        user, password = creds.split(":", 1)
    except (KeyError, ValueError):
        logger.warning(
            "Could not read Github credentials, returning no result")
        return
    auth = requests.auth.HTTPBasicAuth(user, password)
    github_query = {
        "q": "def+{}+language:python".format("+".join(query.split()))
    }

    logger.info('Querying github search api with "%s"', github_query["q"])
    try:
        r = requests.get(
            GITHUB_SEARCH_URL, params=github_query, auth=auth)
        r.raise_for_status()
        api_response = r.json()
    except (requests.exceptions.RequestException, ValueError) as err:
        logger.warning("Failed to query github search API: {}".format(err))
        return

    for item in api_response.get("items", []):
        try:
            r = requests.get(item["url"], auth=auth)
            r.raise_for_status()
            response = r.json()
        except (requests.exceptions.RequestException, ValueError) as err:
            logger.warning("Failed to query github API: {}".format(err))
            continue

        try:
            code = base64.b64decode(response["content"]).decode()
        except (KeyError, ValueError) as err:
            logger.warning("Failed to decode github API reponse: {}"
                           .format(err))
            continue

        yield GithubAnswer(code)
