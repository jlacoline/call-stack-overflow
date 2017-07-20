import os
import requests
import html
import re
import logging

from google import search


level = logging.DEBUG if os.environ.get("CALLSTACKOVERFLOW_DEBUG") \
    else logging.INFO
logging.basicConfig(format="%(message)s", level=level)
logger = logging.getLogger("callstackoverflow")

# Credits to Filip Haglund for stackoverflow html parsing
# https://github.com/drathier/stack-overflow-import
def _find_code_in_html(s):
    answers = re.findall(r'<div id="answer-.*?</table', s, re.DOTALL)
    for answer in answers:
        codez = re.finditer(r"<pre[^>]*>[^<]*<code[^>]*>((?:\s|[^<]|<span[^>]*>[^<]+</span>)*)</code></pre>", answer)
        codez = map(lambda x: x.group(1), codez)
        for code in sorted(codez, key=lambda x: -len(x)):
            code = html.unescape(code)
            code = re.sub(r"<[^>]+>([^<]*)<[^>]*>", "\1", code)
            yield code


def _search_for_def_keyword(names, code):
    for name in names:
        if "def {}(".format(name) in code:
            logger.debug ("Found function definition in code")
            logger.debug(code)
            try:
                # try to exec code
                scope = {}
                exec(code, scope)
                yield scope[name]
            except Exception:  # any exception
                logger.debug("Code execution failed")

def _generate_potential_names_from_query(query):
    return set([query.lower().replace(" ", ""),
                query.lower().replace(" ", "_"),
                query.lower().split()[0]])

def get_function(query, test_func=None, func_names=None):
    if func_names is None:
        func_names = _generate_potential_names_from_query(query)

    # search on google
    links = search("site:stackoverflow.com python {}".format(query), stop=1)

    # get html from stackoverflow and parse it
    for link in links:
        logger.debug("Trying %s", link)
        raw_html = requests.get(link).text
        for code in _find_code_in_html(raw_html):
            for func in _search_for_def_keyword(func_names, code):
                # execute tests
                if test_func is not None:
                    try:
                        assert test_func(func)
                    except Exception:
                        logger.debug("Tests failed")
                        continue
                    logger.debug("Tests passed!")
                return func

def call_stackoverflow(query, *args, **kwargs):
    result = {}
    def does_it_crash(f):
        try:
            result["out"] = f(*args, **kwargs)
        except Exception:
            return False
        return True
    get_function(query, does_it_crash)
    if "out" in result:
        return result["out"]
    else:
        raise NameError("No function found for {}".format(query))
