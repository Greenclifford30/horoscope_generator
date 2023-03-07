# syntax=docker/dockerfile:1

FROM python:alpine3.16
WORKDIR /faceless_youtube
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0"]