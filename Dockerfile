FROM python:3.7.12-slim-bullseye

WORKDIR /covid-19-analysis

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["streamlit", "run"]

CMD ["app.py", "--server.port", "80"]