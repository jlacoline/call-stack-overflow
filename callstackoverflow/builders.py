import re
import ast
import copy
from itertools import permutations
from functools import reduce
from operator import add
import logging

logger = logging.getLogger(__name__)


def get_function_from_code(code, name):
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


def search_for_def_keyword(code):
    for name in re.findall(r"def ([^\(]+)\(", code):
        yield get_function_from_code(code, name)


def make_function_from_shell_script(code):
    lines = code.splitlines()
    # if prompt characters are dectected,remove them
    for prompt in [r"^>>> (.*)", r"^In\ [\d+\]: (.*)"]:
        if any(map(lambda l:  re.match(prompt, l), lines)):
            lines = map(lambda l: re.sub(prompt, r"\1", l).strip()
                        if re.match(prompt, l) else "", lines)
            break
    # remove empty lines
    lines = list(filter(lambda l: l, lines))

    # format last line. TODO implement this in ast
    if lines:
        # remove the "print" instruction if found
        lines[-1] = re.sub(r"^print\s*\(([^\)]*)\)", r"\1", lines[-1]).strip()
        lines[-1] = re.sub(r"^print\s+(.*)", r"\1", lines[-1]).strip()
        # remove variable assignement if found
        lines[-1] = re.sub(r"^[^=]+\s*=(.*)", r"\1", lines[-1]).strip()
        # add a "return" statement
        lines[-1] = "return {}".format(lines[-1])

    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError as err:
        logger.debug("ast parsing failed: %s", err)
        raise StopIteration()
    params = _ast_parametrize_constants(tree)
    logsuccess = False
    for deftree in _add_func_def_to_ast_tree(tree, params):
        scope = {}
        try:
            exec(compile(deftree, "<string>", "exec"), scope)
        except Exception as err:
            logger.debug("building function from shell script failed: %s", err)
            raise StopIteration()
        if not logsuccess:
            logger.info("Successfully built a fonction from shell script")
            logsuccess = True
        yield scope["__function_from_shell_script__"]


def _add_func_def_to_ast_tree(tree, params):
    for permutation in permutations(range(len(params))):
        newtree = copy.deepcopy(tree)
        newtree.body = [ast.FunctionDef(
            name="__function_from_shell_script__",
            args=ast.arguments(
                args=[ast.arg(arg=params[i][0]) for i in permutation],
                defaults=[params[i][1] for i in permutation],
                kw_defaults=[], kwarg=None, kwonlyargs=[], vararg=None),
            body=newtree.body,
            decorator_list=[])]
        ast.fix_missing_locations(newtree)
        yield newtree


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
