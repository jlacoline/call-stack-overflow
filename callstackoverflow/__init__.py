import os
import requests
import html
import re
import logging
import logging.config
import itertools

from google import search


level = os.environ.get("CALLSTACKOVERFLOW_LOGLEVEL", logging.CRITICAL)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {'format': '%(asctime)s - %(levelname)s - %(message)s'}},
    'level': level,
    'loggers': {'': {'handlers': ['default'], 'level': level}},
    'handlers': {'default': {
        'level': level,
        'formatter': 'default',
        'class': 'logging.StreamHandler'}}
})
logger = logging.getLogger("callstackoverflow")

RE_ANSWER = re.compile(r'<div id="answer-.*?</table', re.DOTALL)
RE_CODE = re.compile(
    r"<pre[^>]*>[^<]*<code[^>]*>((?:\s|[^<]|<span[^>]*>[^<]+</span>)*)"
    r"</code></pre>")
RE_DOC_URL = re.compile(
    r"<a href=([\"\']https://docs\.python\.org"
    r"/(?:\d/)?library/([^#]*).html#([^\"^\']*))[\"\']")


# Credits to Filip Haglund for stackoverflow html parsing
# https://github.com/drathier/stack-overflow-import
def _find_code_in_html(s):
    answers = re.findall(RE_ANSWER, s)
    for answer in answers:
        codez = re.finditer(RE_CODE, answer)
        codez = map(lambda x: x.group(1), codez)
        for code in sorted(codez, key=lambda x: -len(x)):
            code = html.unescape(code)
            yield code


def _find_doc_url_in_html_and_make_code(raw_url):
    answers = re.findall(RE_ANSWER, raw_url)
    for answer in answers:
        for match in re.finditer(RE_DOC_URL, answer):
            lib, func = match.group(2), match.group(3)
            code = """
try:
    import {}
except Exception:
    pass

def code_from_python_doc(*args, **kwargs):
    return {}(*args, **kwargs)
            """.format(lib, func)
            yield code


def _search_for_def_keyword(names, code):
    for name in names:
        if "def {}(".format(name) in code:
            logger.debug("Trying out this code:\n%s", code)
            try:
                # try to exec code
                scope = {}
                exec(code, scope)
                yield scope[name]
            except Exception as err:
                logger.debug("Code execution failed: %s", err)


def _generate_potential_names_from_query(query):
    return list(set([query.lower().replace(" ", ""),
                    query.lower().replace(" ", "_"),
                    query.lower().split()[0]]))


def _make_function_from_shell_script(code, name):
    # keep only lines begining with ">>>"
    lines = filter(lambda l:  l.startswith(">>>"), code.splitlines())
    # remove ">>>"
    lines = map(lambda l: l.replace(">>>", "").strip(), lines)
    # remove empty lines (some answers may contain empty prompt lines)
    lines = filter(lambda l: l, lines)
    # add the "return" statement to the last instruction
    if lines:
        lines = list(lines)
        lines[-1] = "return {}".format(lines[-1])
    # indent lines
    lines = map(lambda l: "    "+l, lines)
    return "def {}():\n{}".format(name, "\n".join(lines))


def get_function(query, test_func=None, func_names=None):
    if not func_names:
        func_names = _generate_potential_names_from_query(query)
    func_names.append("code_from_python_doc")  # super ugly, refactor asap

    # search on google
    google_query = "site:stackoverflow.com python {}".format(query)
    logger.info('Querying google with "%s"', google_query)
    links = search(google_query, stop=1)

    # get html from stackoverflow and parse it
    for link in links:
        logger.info("Parsing stackoverflow answers at %s", link)
        raw_html = requests.get(link).text
        for code in itertools.chain(
                _find_code_in_html(raw_html),
                _find_doc_url_in_html_and_make_code(raw_html)):
            if code.startswith(">>>"):
                code = _make_function_from_shell_script(code, func_names[0])
            for func in _search_for_def_keyword(func_names, code):
                logger.info("Found callable function, lauching tests")
                # execute tests
                if test_func is not None:
                    try:
                        test_func(func)
                    except Exception as exc:
                        logger.debug("Tests failed: %s", exc)
                        continue
                    logger.info("Tests passed! Returning function")
                return func


def call_stack_overflow(query, *args, **kwargs):
    result = {}

    def does_it_crash(f):
        result["out"] = f(*args, **kwargs)

    get_function(query, does_it_crash)
    if "out" in result:
        return result["out"]
    else:
        raise NameError('No result found for "{}"'.format(query))
