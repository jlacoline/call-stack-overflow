FROM python:3.6.5-alpine

RUN pip install dill
COPY entrypoint.py /entrypoint.py

ENTRYPOINT ["python", "/entrypoint.py"]
