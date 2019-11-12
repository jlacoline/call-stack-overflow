import callstackoverflow as cso


def test_first_result_calls():
    assert cso.call_stack_overflow("quick sort", [1, 3, 2, 5, 4]) == \
        [1, 2, 3, 4, 5]
    assert cso.call_stack_overflow("fibonacci", 7) == 13

def test_lambda_calls():
    # string splitting
    split_string = cso.get_function("split string", lambda f: f("hello world") == ["hello", "world"])
    assert split_string("hello python world") == ["hello", "python", "world"]
    assert split_string("1 2 3 4 5 6 7 8 9") == ["1", "2", "3", "4", "5", "6" , "7", "8", "9"]

    # GCD
    gcd = cso.get_function("gcd", lambda f: f(20,30) == 10)
    assert gcd(12,8) == 4
    assert gcd(15,9) == 3

    # removing newline at the end of a string
    for description in ["remove \\n from string",
                        "remove newline from string"]:
        newline_remover = cso.get_function(
            description, lambda f: f("hello new line\n") == "hello new line")
        assert newline_remover("remove backslash n\n") == "remove backslash n"

    # removing any substring from a string
    # substring_remover = cso.get_function(
    #     "remove substring",
    #     lambda f: f("hello new line\n", "\n") == "hello new line")
    # assert newline_remover("remove foo", "foo") == "remove "
    # assert newline_remover("aa bb cc aa cc", "aa") == " bb cc  cc"


if __name__ == "__main__":  # no need of pytest for the moment
    test_lambda_calls()
    test_first_result_calls()
    print("*****TESTS SUCCEEDED*****")
