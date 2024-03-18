FROM python:3.10-slim

WORKDIR /app
RUN pip install -U pip
RUN pip install streamlit==1.32.2 streamlit_code_editor==0.1.12 streamlit-monaco==0.1.3

ENTRYPOINT ["streamlit", "run", "Home.py"]
