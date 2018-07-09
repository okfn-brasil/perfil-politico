# Perfil 

A platform for profiling public figures in Brazilian politics, 
searching for weird patterns or figures with inconsistent politics paths 
(changes in parties, unpopular law projects, high expenses on public money). 

## Settings

To run the API, you must copy the `env-template` to a `.env` file and
add the MongoDB URL.

## Docker install

Starting the application:

```sh
$ docker-compose up
```

The API will be available at [`localhost:8000`](http://localhost:8000) and the
notebooks at [`localhost:8888`](http://localhost:8888).

To run the API tests:

```sh
$ docker-compose run --rm api sh
```

## Local install

Project is currently developed in Python `3.6.1`

### Dependencies

Add dependencies:

```
$ pip install -r api/requirements.txt
$ pip install -r notebooks/requirements.txt
```

### API

Run the api:

```
$ python api/manage.py runserver
```

Run api tests:

```
$ cd api
$ pytest
```
