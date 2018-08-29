FROM python:3.7.0-alpine

ENV SECRET_KEY=temporary-secret-key-to-generate-staticfiles
WORKDIR /code

COPY manage.py manage.py
COPY requirements.txt requirements.txt

RUN apk update && \
    apk --no-cache add libpq && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps g++ gcc musl-dev postgresql-dev && \
    python -m pip --no-cache install -U pip && \
    python -m pip --no-cache install -r requirements.txt && \
    apk --purge del .build-deps && \
    rm -rfv /var/cache/apk/*

COPY .coveragerc .coveragerc
COPY perfil/ perfil/
RUN python manage.py collectstatic --no-input

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
