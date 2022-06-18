import ast
import re
import copy
from itertools import permutations, islice
from functools import reduce
from operator import add
import logging

logger = logging.getLogger(__name__)

PERMUTATIONS_LIMIT = 20

PYTHON_PROMPT_PREFIX = re.compile(r"^>>> (.*)")
IPYTHON_PROMPT_PREFIX = re.compile(r"^In \[\d+\]: (.*)")

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


class ConstTransformer(ParamRegisterer):
    def visit_Constant(self, node):
        name = self._add_param("const", node)
        return ast.copy_location(ast.Name(name, ast.Load()), node)


class ConstAndListTransformer(ConstTransformer):
    def visit_List(self, node):
        name = self._add_param("list", node)
        return ast.copy_location(ast.Name(name, ast.Load()), node)


class ConstAndListAndDictTransformer(ConstAndListTransformer):
    def visit_Dict(self, node):
        name = self._add_param("dict", node)
        return ast.copy_location(ast.Name(name, ast.Load()), node)


def build_from_shell_script(code):
    lines = code.splitlines()
    # if prompt characters are detected,remove them
    for prompt_prefix_re in [PYTHON_PROMPT_PREFIX, IPYTHON_PROMPT_PREFIX]:
        if any(map(lambda l:  re.match(prompt_prefix_re, l), lines)):
            lines = map(lambda l: re.sub(prompt_prefix_re, r"\1", l).strip()
                        if re.match(prompt_prefix_re, l) else "", lines)
            break
    # remove empty lines
    lines = list(filter(lambda l: l.strip() != "", lines))

    try:
        tree = ast.parse("\n".join(lines))
    except SyntaxError as err:
        logger.debug("ast parsing failed: %s", err)
        return
    logsuccess = False

    # add "return" to the last statement
    end_with_return(tree)

    # modify the ast tree by transforming elements into function parameters
    # 1st run only turns constants into parameters
    # 2nd run also turns lists into parameters
    # 3rd run also turns dicts into parameters
    for transformer_class in [
            ConstTransformer, ConstAndListTransformer,ConstAndListAndDictTransformer]:
        paramtree = copy.deepcopy(tree)
        transformer = transformer_class()
        transformer.visit(paramtree)

        # transform the tree into a function definition
        # try with different argument orders
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


# Modifies the given ast tree in place to add "return" to the last statement
def end_with_return(tree):
    if not tree.body:
        return

    last_statement = tree.body[-1]

    # do nothing if the last statement is already a return instruction
    if type(last_statement) == ast.Return:
        return

    if type(last_statement) == ast.Expr:
        last_value = last_statement.value

        # if the last statement is a print, remove the print call and return the first argument
        # TODO: what about print calls like `print(f"The answer is {answer}")` ?
        if type(last_value) == ast.Call \
                and type(last_value.func) == ast.Name \
                and last_value.func.id == 'print':

            if last_value.args:
                last_value = last_value.args[0]
    elif type(last_statement) == ast.Assign:
        # if the last statement is a variable assignement, remove the assignement and return the value
        last_value = last_statement.value
    else:
        last_value = last_statement

    # add the return instruction
    tree.body[-1] = ast.Return(last_value)


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
