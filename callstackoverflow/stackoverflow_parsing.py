import re

from bs4 import BeautifulSoup

from .builders import PYTHON_DOCS_URL_REGEXP



def find_stackoverflow_answers(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')  # TODO try except
    answers_tags = soup.find_all("div", id=re.compile(r"answer-.*"))
    for answer_tag in answers_tags:
        yield StackOverflowAnswer(answer_tag)


class StackOverflowAnswer:
    def __init__(self, bs_tag):
        self._tag = bs_tag

    def code_blocks(self):
        blocks = self._tag.find_all("code")
        for block in blocks:
            yield block.text

    def doc_links(self):
        for link in self._tag.find_all("a", href=PYTHON_DOCS_URL_REGEXP):
            yield link["href"]