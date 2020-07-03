FROM python:3.8.3-slim-buster

COPY requirements.txt requirements.txt
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev && \
    pip install -r requirements.txt

WORKDIR /app
COPY src .

CMD ["python", "main.py"]
