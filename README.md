[![Travis CI](https://img.shields.io/travis/okfn-brasil/perfil.svg)](https://travis-ci.org/okfn-brasil/perfil)
[![Codecov](https://img.shields.io/codecov/c/github/okfn-brasil/perfil.svg)](https://codecov.io/gh/okfn-brasil/perfil)
[![Code Climate](https://img.shields.io/codeclimate/maintainability/okfn-brasil/perfil.svg)](https://codeclimate.com/github/okfn-brasil/perfil)

# Perfil

A platform for profiling public figures in Brazilian politics,
searching for weird patterns or figures with inconsistent politics paths
(changes in parties, unpopular law projects, high expenses on public money).

## Install

This project requires [Docker](https://docs.docker.com/install/) and
[Docker Compose](https://docs.docker.com/compose/install/).

### Settings

To run the API, you must copy the `env-template` to a `.env` file and
edit it accordingly.

### Running

Starting the application:

```sh
$ docker-compose up
```

The API will be available at [`localhost:8000`](http://localhost:8000) and the
notebooks at [`localhost:8888`](http://localhost:8888).

### Database

#### Initial setup

You should create your database by applying migrations:

```sh
$ docker-compose run django ./manage.py migrate
```

You can also create a super user so you can access your
[Django admin site](https://docs.djangoproject.com/en/2.0/ref/contrib/admin/)
in [`localhost:8000/admin/`](http://localhost:8000/admin/):

```sh
$ docker-compose run django ./manage.py createsuperuser
```

#### Bringing data in

The database can be populated by Django commands such as `load_people`,
`load_parties`, `load_elections`, etc. To check the full list try:

```sh
$ docker-compose run --rm django ./manage.py --help | grep load_
```

Your local `data/` directory is mapped, inside the container, to `/mnt/data`.
Each command uses a CSV from a public and available source. Use `--help` for
more info.

You must pass the path to a CSV file together with the command. For example:

```sh
$ docker-compose run django ./manage.py load_people /mnt/data/candidates.csv
```

## Tests

```sh
$ docker-compose run django py.test
$ docker-compose run django black . --check
```
