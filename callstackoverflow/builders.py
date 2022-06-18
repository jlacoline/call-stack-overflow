import re
import logging

from .shell_script_parser import build_from_shell_script

logger = logging.getLogger(__name__)

# regexp used to identify python documentation links
PYTHON_DOCS_URL_REGEXP = re.compile(
    r"https?://docs\.python\.org/(?:\d/)?library/([^#]*).html#(.*)")


def _get_function_from_code(code, name):
    try:
        # try to exec code
        scope = {}
        exec(code, scope)
    except Exception as err:
        logger.debug("Code execution failed: %s", err)
        return None
    try:
        fun = scope[name]
        assert(callable(fun))
        return fun
    except (KeyError, AssertionError):
        logger.debug('could not find a function named "{}" in code'
                     .format(name))


def search_for_def_keyword(answer):
    for code in answer.code_blocks():
        logger.info(
            "Trying to find function definitions in this code:\n%s", code)
        for name in re.findall(r"def ([^\(]+)\(", code):
            yield _get_function_from_code(code, name)


def make_functions_from_shell_scripts(answer):
    for code in answer.code_blocks():
        logger.info(
            "Trying to build a fonction from this shell script:\n%s", code)
        for fun in build_from_shell_script(code):
            yield fun


def make_functions_from_documentation_links(answer):

    for doc_link in answer.doc_links():
        match = PYTHON_DOCS_URL_REGEXP.match(doc_link)
        if match is None:
            continue
        lib = match.group(1)
        name = match.group(2)

        logger.info("Trying to make a function from this "
                    "documentation link: %s", doc_link)

        code = """
try:
    import {}
except Exception:
    pass

def __code_from_python_doc__(*args, **kwargs):
    return {}(*args, **kwargs)
        """.format(lib, name)
        yield _get_function_from_code(code, "__code_from_python_doc__")
