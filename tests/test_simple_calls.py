import callstackoverflow as cso


def test_first_result_calls():
    assert cso.call_stack_overflow("quick sort", [1, 3, 2, 5, 4]) == \
        [1, 2, 3, 4, 5]
    assert cso.call_stack_overflow("fibonacci", 7) == 13


def test_lambda_calls():
    # string splitting
    split_string = cso.get_function(
        "split string",
        lambda f: f("hello world") == ["hello", "world"])
    assert split_string("hello python world") == ["hello", "python", "world"]
    assert split_string("1 2 3 4 5 6 7 8 9") == [
        "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    # GCD
    gcd = cso.get_function("gcd", lambda f: f(20, 30) == 10,
                           methods=[cso.M_SEARCH_FOR_DEF])
    assert gcd(12, 8) == 4
    assert gcd(15, 9) == 3

    # removing newline at the end of a string
    for description in ["remove \\n from string",
                        "remove newline from string"]:
        newline_remover = cso.get_function(
            description, lambda f: f("hello new line\n") == "hello new line",
            methods=[cso.M_PARSE_SHELL_SCRIPTS])
        assert newline_remover("remove backslash n\n") == "remove backslash n"

    log2 = cso.get_function("log 2", lambda f: f(8) == 3,
                            methods=[cso.M_READ_DOCUMENTATION_LINKS])
    assert log2(32) == 5
    assert log2(512) == 9


if __name__ == "__main__":  # no need for pytest at the moment
    test_lambda_calls()
    test_first_result_calls()
    print("*****TESTS SUCCEEDED*****")
