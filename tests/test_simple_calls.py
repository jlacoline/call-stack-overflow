from callstackoverflow import call_stack_overflow


def test_simple_calls():
    assert call_stack_overflow("quick sort", [1, 3, 2, 5, 4]) == \
        [1, 2, 3, 4, 5]
    assert call_stack_overflow("split string", "hello python world") == \
        ["hello", "python", "world"]
    assert call_stack_overflow("gcd", 20, 30) == 10
    assert call_stack_overflow("fibonacci", 7) == 13
    assert "hello new line" == \
        call_stack_overflow('remove \\n from string',
                            "hello new line\n") == \
        call_stack_overflow('remove newline from string',
                            "hello new line\n") == \
        call_stack_overflow('remove expression from string',
                            "hello new line\n",
                            "\n")


if __name__ == "__main__":  # no need of pytest for the moment
    test_simple_calls()
    print("*****TESTS SUCCEEDED*****")
