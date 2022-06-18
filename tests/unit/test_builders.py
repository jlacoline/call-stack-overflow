import callstackoverflow as cso

# helper funcion for this test file
# checks that at least one function generated from the builder passes the given "fn_test"
def _expect_success(builder, fn_test, answer_code_block=None, answer_doc_link=None):

    # some mock of StackOverflowAnswer/GithubAnswer objects
    class FakeAnswer:
        def code_blocks(self):
            if answer_code_block is not None:
                yield answer_code_block

        def doc_links(self):
            if answer_doc_link is not None:
                yield answer_doc_link


    for generated_function in builder(FakeAnswer()):
        try:
            assert fn_test(generated_function)
        except Exception:
            continue
        return

    raise AssertionError(f"no valid function generated for this answer:\ncode block: \n{answer_code_block}\ndoc link:\n  {answer_doc_link}")


def test_build_from_def_keyword_search():

    for code_block in [
        # simple function
        '''
def my_splitter(my_string, my_separator):
    return my_string.split(my_separator)
        ''',
        # same function with a lot of garbage around it
        '''
# useless code before the function definition
list(i for i in range(10) if i%2)

# some comment about the function
def my_splitter(my_string, my_separator):
    return my_string.split(my_separator)

# some example
print(my_splitter("a-b-c", "-"))
        '''
    ]:
        _expect_success(
            cso.builders.search_for_def_keyword,
            lambda f: f("iXloveXrefrigerators", "X") == ["i", "love", "refrigerators"],
            answer_code_block=code_block
            )


def test_build_from_shell_script():

    for code_block in [
        # simple one line response
        '''
"mystring".split("mychar")
        ''',

        # code with comments and print() calls
        '''
# some cool comment
some_string = "aaa-bbb-ccc-ddd"
separator = "-"

print(some_string.split(separator))
# ["aaa", "bbb", "ccc", "ddd"]
        ''',

        # ending with just a value
        '''
sep = "/"
splitted = "a/b/c".split(sep)

splitted
        ''',

        # python prompt
        '''
>>> print("a".split("b"))
        ''',

        # ipython prompts
        '''
In [1]: s = "cool string"

In [2]: s.split(" ")
Out[2]: ['cool', 'string']
        '''
    ]:
        _expect_success(
            cso.builders.make_functions_from_shell_scripts,
            lambda f: f("iXloveXrefrigerators", "X") == ["i", "love", "refrigerators"],
            answer_code_block=code_block
            )


def test_build_from_doc_link():
    _expect_success(
        cso.builders.make_functions_from_documentation_links,
        lambda f: f("iXloveXrefrigerators", "X") == ["i", "love", "refrigerators"],
        answer_doc_link="https://docs.python.org/2/library/stdtypes.html#str.split"
        )