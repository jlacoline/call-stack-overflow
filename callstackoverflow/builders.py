import logging

logger = logging.getLogger(__name__)


def get_function_from_code(code, name):
    if "def {}(".format(name) in code:
        logger.debug("Trying to exec this this code:\n%s", code)
        try:
            # try to exec code
            scope = {}
            exec(code, scope)
            return scope[name]
        except Exception as err:
            logger.debug("Code execution failed: %s", err)


def make_function_from_shell_script(code):
    # keep only lines begining with ">>>"
    lines = list(filter(lambda l:  l.startswith(">>>"), code.splitlines()))
    if not lines:
        return None
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
    defcode = "def {}():\n{}".format("__function_from_shell_script__",
                                     "\n".join(lines))
    return get_function_from_code(defcode, "__function_from_shell_script__")


def make_function_from_documentation(lib, name):
    code = """
try:
    import {}
except Exception:
    pass

__code_from_python_doc__ = {}
    """.format(lib, name)
    return get_function_from_code(code, "__code_from_python_doc__")
