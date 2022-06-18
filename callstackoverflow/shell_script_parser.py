import ast
import re
import copy
from itertools import permutations, islice
from functools import reduce
from operator import add
import logging

logger = logging.getLogger(__name__)

PERMUTATIONS_LIMIT = 20

GENERATED_FUNCTION_NAME = "__function_from_shell_script__"


class ParamRegisterer(ast.NodeTransformer):
    def __init__(self):
        self._params = {}

    def _add_param(self, type_, default):
        current = self._params.setdefault(type_, [])
        name = "__{}_arg_{}__".format(type_, len(current))
        current.append((name, default))
        return name

    def params(self):
        return reduce(add, self._params.values(), [])


class StrNumTransformer(ParamRegisterer):
    def visit_Str(self, node):
        name = self._add_param("str", node)
        return ast.copy_location(ast.Name(name, ast.Load()), node)

    def visit_Num(self, node):
        name = self._add_param("num", node)
        return ast.copy_location(ast.Name(name, ast.Load()), node)


class StrNumListTransformer(StrNumTransformer):
    def visit_List(self, node):
        name = self._add_param("list", node)
        return ast.copy_location(ast.Name(name, ast.Load()), node)


class StrNumListDictTransformer(StrNumListTransformer):
    def visit_Dict(self, node):
        name = self._add_param("dict", node)
        return ast.copy_location(ast.Name(name, ast.Load()), node)


def build_from_shell_script(code):
    lines = code.splitlines()
    # if prompt characters are dectected,remove them
    for prompt in [r"^>>> (.*)", r"^In \[\d+\]: (.*)"]:
        if any(map(lambda l:  re.match(prompt, l), lines)):
            lines = map(lambda l: re.sub(prompt, r"\1", l).strip()
                        if re.match(prompt, l) else "", lines)
            break
    # remove empty lines
    lines = list(filter(lambda l: l.strip() != "", lines))

    # format last line.
    if lines:
        lines[-1] = clean_last_statement(lines[-1])

    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError as err:
        logger.debug("ast parsing failed: %s", err)
        return
    logsuccess = False
    for transformer_class in [StrNumListDictTransformer, StrNumListTransformer,
                              StrNumTransformer]:
        paramtree = copy.deepcopy(tree)
        transformer = transformer_class()
        transformer.visit(paramtree)
        for deftree in add_func_def_to_tree(paramtree, transformer.params()):
            scope = {}
            try:
                exec(compile(deftree, "<string>", "exec"), scope)
            except Exception as err:
                logger.debug(
                    "building function from shell script failed: %s", err)
                return  # exiting immediately, because there's no reason that the compilation will work with other parameter permutations
            if not logsuccess:
                logger.info("Successfully built a fonction from shell script")
                logsuccess = True
            yield scope[GENERATED_FUNCTION_NAME]


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


def add_func_def_to_tree(tree, params):
    _permutations = permutations(range(len(params)))
    # limit the number of permutations to avoid huge loops
    _permutations = islice(_permutations, 0, PERMUTATIONS_LIMIT)
    for permutation in _permutations:
        newtree = copy.deepcopy(tree)
        newtree.body = [ast.FunctionDef(
            name=GENERATED_FUNCTION_NAME,
            args=ast.arguments(
                args=[ast.arg(arg=params[i][0]) for i in permutation],
                defaults=[params[i][1] for i in permutation],
                kw_defaults=[], kwarg=None, kwonlyargs=[], vararg=None, posonlyargs=[]),
            body=newtree.body,
            decorator_list=[])]
        ast.fix_missing_locations(newtree)
        yield newtree
