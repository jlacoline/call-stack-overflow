import os
import logging
import logging.config


from .builders import search_for_def_keyword, \
                      make_function_from_shell_script, \
                      make_function_from_documentation
from . import stackoverflow_parsing as parser
from .testers import apply_tests
from . import web

M_SEARCH_FOR_DEF = "search for def keyword"
M_PARSE_SHELL_SCRIPTS = "parse shell scripts"
M_READ_DOCUMENTATION_LINKS = "read documentation links"
M_ALL = [M_SEARCH_FOR_DEF, M_PARSE_SHELL_SCRIPTS, M_READ_DOCUMENTATION_LINKS]


level = os.environ.get("CALLSTACKOVERFLOW_LOGLEVEL", logging.CRITICAL)
logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(levelname)s - %(name)s - %(message)s'}},
    'loggers': {'': {'handlers': ['default'], 'level': level},
                'urllib3': {'level': logging.WARNING}},
    'handlers': {'default': {
        'level': level,
        'formatter': 'default',
        'class': 'logging.StreamHandler'}}
})
logger = logging.getLogger(__name__)


def get_function(query, tester=None, methods=M_ALL):
    if not methods:
        return None

    def _validate(fun):
        return fun is not None and apply_tests(fun, tester)

    for answer in web.fetch_stackoverflow_answers(query):
        if M_READ_DOCUMENTATION_LINKS in methods:
            for doc in parser.find_documentation_url_in_answer(answer):
                logger.debug("Trying to make a function from this "
                             "documentation link: %s", doc["link"])
                f = make_function_from_documentation(doc["lib"], doc["func"])
                if _validate(f):  # UGLY replicated code
                    return f
        if M_SEARCH_FOR_DEF in methods or M_PARSE_SHELL_SCRIPTS in methods:
            for code in parser.find_code_in_answer(answer):
                logger.debug("Trying this code:\n%s", code)
                if M_SEARCH_FOR_DEF in methods:
                    for f in search_for_def_keyword(code):
                        if _validate(f):
                            return f
                if M_PARSE_SHELL_SCRIPTS in methods:
                    for f in make_function_from_shell_script(code):
                        if _validate(f):
                            return f


def call_stack_overflow(query, *args, **kwargs):
    result = {}

    def just_run_it(f):
        result["out"] = f(*args, **kwargs)

    if get_function(query, just_run_it) is not None:
        return result["out"]
    else:
        raise NameError('No result found for "{}"'.format(query))
