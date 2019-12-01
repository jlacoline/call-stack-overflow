import callstackoverflow as cso


def test_lambda_calls():
    split_string = cso.get_function(
        "split string",
        lambda f: f("hello world") == ["hello", "world"])
    assert split_string("hello python world") == ["hello", "python", "world"]
    assert split_string("1 2 3 4 5 6 7 8 9") == [
        "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    reverser = cso.get_function("reverse list",
                                lambda f: f([1, 2, 3]) == [3, 2, 1])
    assert reverser([4, 6, 3, 2]) == [2, 3, 6, 4]


def test_method_search_for_def():
    gcd = cso.get_function("gcd", lambda f: f(20, 30) == 10,
                           methods=[cso.M_SEARCH_FOR_DEF])
    assert gcd(12, 8) == 4
    assert gcd(15, 9) == 3


def test_method_parse_shell_script():
    for description in ["remove \\n from string",
                        "remove newline from string"]:
        newline_remover = cso.get_function(
            description, lambda f: f("hello new line\n") == "hello new line",
            methods=[cso.M_PARSE_SHELL_SCRIPTS])
        assert newline_remover("remove backslash n\n") == "remove backslash n"


def test_method_read_doc():
    log2 = cso.get_function("log 2", lambda f: f(8) == 3,
                            methods=[cso.M_READ_DOCUMENTATION_LINKS])
    assert log2(32) == 5
    assert log2(512) == 9


def test_first_result_calls():
    assert cso.call_stack_overflow("quick sort", [1, 3, 2, 5, 4]) == \
        [1, 2, 3, 4, 5]
    assert cso.call_stack_overflow("fibonacci", 7) == 13


def test_github_calls():
    fibo = cso.get_function(
        "fibonacci", lambda f: f(7) == 13, sources=[cso.S_GITHUB],
        methods=[cso.M_SEARCH_FOR_DEF])
    assert fibo(5) == 5


def test_docker_tester():
    tester = cso.testers.DockerTester()
    fibo = cso.get_function(
        "fibonacci", lambda f: f(7) == 13,
        methods=[cso.M_SEARCH_FOR_DEF], tester=tester)
    assert fibo(5) == 5
