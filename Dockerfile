FROM python:3.7.2-alpine

ENV PYTHONBREAKPOINT=ipdb.set_trace
ENV SECRET_KEY=temporary-secret-key-to-generate-staticfiles
WORKDIR /code

COPY manage.py manage.py
COPY requirements.txt requirements.txt

RUN apk update && \
    apk --no-cache add libpq && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps g++ gcc git musl-dev postgresql-dev && \
    python -m pip install -U pip && \
    python -m pip install -r requirements.txt && \
    apk --purge del .build-deps && \
    rm -rfv /var/cache/apk/*

COPY .coveragerc .coveragerc
COPY pytest.ini pytest.ini
COPY perfil/ perfil/
RUN python manage.py collectstatic --no-input

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
