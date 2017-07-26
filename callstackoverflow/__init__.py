import os
import logging
import logging.config


from .builders import get_function_from_code, \
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


def _generate_potential_names_from_query(query):
    return list(set([query.lower().replace(" ", ""),
                    query.lower().replace(" ", "_"),
                    query.lower().split()[0]]))


def get_function(query, tester=None, methods=M_ALL, func_names=None):
    if not methods:
        return None
    if not func_names and M_SEARCH_FOR_DEF in methods:
        func_names = _generate_potential_names_from_query(query)

    f = None

    def _validate():
        return f is not None and apply_tests(f, tester)

    for answer in web.fetch_stackoverflow_answers(query):
        if M_SEARCH_FOR_DEF in methods or M_PARSE_SHELL_SCRIPTS in methods:
            for code in parser.find_code_in_answer(answer):
                if M_SEARCH_FOR_DEF in methods:
                    for name in func_names:
                        f = get_function_from_code(code, name)
                        if _validate():
                            return f
                if M_PARSE_SHELL_SCRIPTS in methods:
                    f = make_function_from_shell_script(code)
                    if _validate():
                        return f
        if M_READ_DOCUMENTATION_LINKS in methods:
            for doc in parser.find_documentation_url_in_answer(answer):
                f = make_function_from_documentation(doc["lib"], doc["func"])
                if _validate():
                    return f


def call_stack_overflow(query, *args, **kwargs):
    result = {}

    def just_run_it(f):
        result["out"] = f(*args, **kwargs)

    if args or kwargs:
        methods = [M_SEARCH_FOR_DEF, M_READ_DOCUMENTATION_LINKS]
    else:
        methods = M_ALL
    if get_function(query, just_run_it, methods=methods) is not None:
        return result["out"]
    else:
        raise NameError('No result found for "{}"'.format(query))
