FROM python:3.13-slim

RUN apt-get update && apt-get install -y gcc g++

WORKDIR /app
RUN pip install -U pip
RUN pip install streamlit==1.45.0 streamlit-monaco==0.1.3

ENTRYPOINT ["streamlit", "run", "app.py"]
