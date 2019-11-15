#!/bin/sh

timeout -t "$TEST_TIMEOUT" python /main.py "$@"
