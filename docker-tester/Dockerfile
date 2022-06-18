FROM python:3.10.5-alpine

ENV TEST_TIMEOUT 30

RUN pip install dill
COPY entrypoint.sh /entrypoint.sh
COPY main.py /main.py

ENTRYPOINT ["/entrypoint.sh"]
