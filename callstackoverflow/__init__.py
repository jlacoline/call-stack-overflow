import os
import logging
import logging.config

from . import builders
from .testers import apply_tests
from . import web

M_SEARCH_FOR_DEF = builders.search_for_def_keyword
M_PARSE_SHELL_SCRIPTS = builders.make_functions_from_shell_scripts
M_READ_DOCUMENTATION_LINKS = builders.make_functions_from_documentation_links
M_ALL = [M_READ_DOCUMENTATION_LINKS, M_SEARCH_FOR_DEF, M_PARSE_SHELL_SCRIPTS]

S_STACKOVERFLOW = web.fetch_stackoverflow_answers
S_GITHUB = web.fetch_github_answers
S_ALL = [S_STACKOVERFLOW, S_GITHUB]


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


def build_functions(query, sources=S_ALL, methods=M_ALL):
    for source in sources:
        for answer in source(query):
            for method in methods:
                for function in method(answer):
                    yield function


def get_function(query, tester, sources=S_ALL, methods=M_ALL):
    for f in build_functions(query, sources=sources, methods=methods):
        if f is not None and apply_tests(f, tester):
            return f
    raise NotImplementedError(
        'No fonction built with query "{}" passed the provided tests'
        .format(query))


def call_stack_overflow(query, *args, **kwargs):
    result = {}

    def just_run_it(f):
        result["out"] = f(*args, **kwargs)
        return True

    get_function(query, just_run_it,
                 methods=[M_SEARCH_FOR_DEF, M_READ_DOCUMENTATION_LINKS])
    return result["out"]
