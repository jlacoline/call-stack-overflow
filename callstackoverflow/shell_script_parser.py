import ast
import re
import copy
from itertools import permutations, islice
from functools import reduce
from operator import add
import logging

logger = logging.getLogger(__name__)

PERMUTATIONS_LIMIT = 120  # = nb of permutations for 5 elements


def build_from_shell_script(code):
    lines = code.splitlines()
    # if prompt characters are dectected,remove them
    for prompt in [r"^>>> (.*)", r"^In \[\d+\]: (.*)"]:
        if any(map(lambda l:  re.match(prompt, l), lines)):
            lines = map(lambda l: re.sub(prompt, r"\1", l).strip()
                        if re.match(prompt, l) else "", lines)
            break
    # remove empty lines
    lines = list(filter(lambda l: l, lines))

    # format last line.
    if lines:
        lines[-1] = clean_last_statement(lines[-1])

    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError as err:
        logger.debug("ast parsing failed: %s", err)
        raise StopIteration()
    params = parametrize_constants(tree)
    logsuccess = False
    for deftree in add_func_def_to_tree(tree, params):
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


#  TODO implement this in ast
def clean_last_statement(raw):
    match = re.match(r"^(\s*)([^\s].*)$", raw)
    indent, content = match.groups()
    # remove the "print" instruction if found
    content = re.sub(r"^print\s*\(([^\)]*)\)", r"\1", content).strip()
    content = re.sub(r"^print\s+(.*)", r"\1", content).strip()
    # remove variable assignement if found
    content = re.sub(r"^[^=]+\s*=(.*)", r"\1", content).strip()
    # add a "return" statement
    content = "return {}".format(content)
    return indent+content


def parametrize_constants(tree):
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


def add_func_def_to_tree(tree, params):
    _permutations = permutations(range(len(params)))
    # limit the number of permutations to avoid huge loops
    _permutations = islice(_permutations, 0, PERMUTATIONS_LIMIT)
    for permutation in _permutations:
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
