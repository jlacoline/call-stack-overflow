import re
import ast
from functools import reduce
from operator import add
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

    try:
        tree = ast.parse("\n".join(lines))
        params = _ast_parametrize_constants(tree)
        tree.body = [ast.FunctionDef(
            name="__function_from_shell_script__",
            args=ast.arguments(
                args=[ast.arg(arg=arg) for arg, _ in params],
                defaults=[default for _, default in params],
                kw_defaults=[], kwarg=None, kwonlyargs=[], vararg=None),
            body=tree.body,
            decorator_list=[])]
        ast.fix_missing_locations(tree)
        scope = {}
        exec(compile(tree, "<string>", "exec"), scope)
        logger.info("Successfully built a fonction from this shell script:\n{}"
                    .format(code))
        return scope["__function_from_shell_script__"]
    except Exception:
        return None


def _ast_parametrize_constants(tree):
    class _NodeTransformer(ast.NodeTransformer):
        def __init__(self):
            self._params = {key: [] for key in ["str", "num"]}

        def visit_Str(self, node):
            name = "__{}_arg_{}__".format("str", len(self._params["str"]))
            self._params["str"].append((name, node))
            return ast.copy_location(ast.Name(name, ast.Load()), node)

        def visit_Num(self, node):
            name = "__{}_arg_{}__".format("num", len(self._params["num"]))
            self._params["num"].append((name, node))
            return ast.copy_location(ast.Name(name, ast.Load()), node)

    transformer = _NodeTransformer()
    transformer.visit(tree)
    return reduce(add, transformer._params.values())


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
