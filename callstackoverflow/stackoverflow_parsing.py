import re

from bs4 import BeautifulSoup


RE_DOC_URL = re.compile(
    r"https?://docs\.python\.org/(?:\d/)?library/([^#]*).html#(.*)")


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
        doc_links = self._tag.find_all("a", href=RE_DOC_URL)
        for doc_link in doc_links:
            # running through the samex regex again, not optimized
            href = doc_link.attrs["href"]
            match = RE_DOC_URL.match(href)
            yield {
                "link": href,
                "lib": match.group(1),
                "name": match.group(2)
            }
