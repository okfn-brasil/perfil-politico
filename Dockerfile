FROM python:3.7.0-alpine

WORKDIR /code

COPY manage.py manage.py
COPY requirements.txt requirements.txt

RUN python -m pip --no-cache install -U pip && \
    python -m pip --no-cache install -r requirements.txt

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
