# Dockerfile, Image, Container
FROM python:3.9

ADD main.py .

RUN pip install fastapi

RUN pip install uvicorn

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0","--port", "80"]
