import html
import re

# Credits to Filip Haglund for the original html code parsing
# https://github.com/drathier/stack-overflow-import
RE_ANSWER = re.compile(r'<div id="answer-.*?</table', re.DOTALL)
RE_CODE = re.compile(
    r"<pre[^>]*>[^<]*<code[^>]*>((?:\s|[^<]|<span[^>]*>[^<]+</span>)*)"
    r"</code></pre>")
RE_DOC_URL = re.compile(
    r"<a href=([\"\']https://docs\.python\.org"
    r"/(?:\d/)?library/([^#]*).html#([^\"^\']*))[\"\']")


def find_answers(raw_html):
    # TODO parse author name
    return re.findall(RE_ANSWER, raw_html)  # finditer?


def find_code_in_answer(answer):
    codez = re.finditer(RE_CODE, answer)
    codez = map(lambda x: x.group(1), codez)
    for code in sorted(codez, key=lambda x: -len(x)):
        code = html.unescape(code)
        yield code


def find_documentation_url_in_answer(answer):
    for match in re.finditer(RE_DOC_URL, answer):
        yield {
            "link": match.group(1),
            "lib": match.group(2),
            "name": match.group(3)
        }
