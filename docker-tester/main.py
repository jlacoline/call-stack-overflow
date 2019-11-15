import sys
import dill
import base64

fn = dill.loads(base64.b64decode(sys.argv[1].encode()))
tester = dill.loads(base64.b64decode(sys.argv[2].encode()))

if not tester(fn):
    raise AssertionError("Test returned False")
