![Travis CI](https://img.shields.io/travis/okfn-brasil/perfil.svg)
![Codecov](https://img.shields.io/codecov/c/github/okfn-brasil/perfil.svg)
![Code Climate](https://img.shields.io/codeclimate/maintainability/okfn-brasil/perfil.svg)

# Perfil

A platform for profiling public figures in Brazilian politics,
searching for weird patterns or figures with inconsistent politics paths
(changes in parties, unpopular law projects, high expenses on public money).

## Settings

To run the API, you must copy the `env-template` to a `.env` file and
edit it accordingly.

## Install

Starting the application:

```sh
$ docker-compose up
```

The API will be available at [`localhost:8000`](http://localhost:8000) and the
notebooks at [`localhost:8888`](http://localhost:8888).

## Initial setup

You should create your database by applying migrations:

```sh
$ docker-compose run django ./manage.py migrate
```

You can also create a super user so you can access your django-admin view in 
`localhost:8000/admin/`:

```sh
$ docker-compose run django ./manage.py createsuperuser 
```

## Filling up the database

The database can be populated by django commands such as `load_people`, 
`load_parties`, `load_elections`, etc. You must pass a csv to the command such 
as:

```sh
$ docker-compose run django ./manage.py load_people candidates.csv
```

Each command uses a CSV from a public and available source. Use `--help` for 
more info.
