FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements.txt /code/

RUN apt-get update && apt-get install -y libhdf5-dev
RUN pip install -r requirements.txt
