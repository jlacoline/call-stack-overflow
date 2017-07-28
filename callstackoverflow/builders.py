import re
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
    lines = code.splitlines()
    # if prompt characters are dectected,remove them
    for prompt in [r"^>>> (.*)", r"^In\[\d+\]: (.*)"]:
        if any(map(lambda l:  re.match(prompt, l), lines)):
            lines = map(lambda l: re.sub(prompt, r"\1", l).strip()
                        if re.match(prompt, l) else "", lines)
            break
    # remove empty lines
    lines = list(filter(lambda l: l, lines))
    # add the "return" statement to the last instruction
    if lines:
        lines[-1] = re.sub(r"^print\s*\(([^\)]*)\)", r"\1", lines[-1]).strip()
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

def __code_from_python_doc__(*args, **kwargs):
    return {}(*args, **kwargs)
    """.format(lib, name)
    return get_function_from_code(code, "__code_from_python_doc__")
