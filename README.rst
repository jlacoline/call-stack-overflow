Just let stackoverflow.com do your job. 

This module builds functions from python code found on stackoverflow.com until it gets the expected result.

.. code-block:: python

  import call_stack_overflow as cso

  # get the first function that passes the provided test
  fibo = cso.get_function("fibonacci", lambda f: f(7) == 13)
  [fibo(n) for n in range(10)]
  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

  # if you are feeling lucky, do not provide any test and execute the first function that comes
  cso.call_stack_overflow("reverse list", [1,2,3,4,5])
  # [5, 4, 3, 2, 1]

  # some examples
  cso.get_function("split string", lambda f: f("hello world") == ["hello", "world"])
  cso.get_function(
      "get the day of the week",
      lambda f: f() in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
  cso.get_function("system os", lambda f: "Linux" in f())
  cso.get_function("quick sort", lambda f: f([1,3,2,6,4,5]) == [1,2,3,4,5,6])

