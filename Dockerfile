FROM python:3.11-bullseye
RUN apt-get update && apt-get install gcc postgresql -y
RUN mkdir /greenhouse
WORKDIR /greenhouse
COPY . /greenhouse/
RUN pip install -r requirements.txt