[![Travis CI](https://img.shields.io/travis/okfn-brasil/perfil-politico.svg)](https://travis-ci.com/okfn-brasil/perfil-politico)
[![Codecov](https://img.shields.io/codecov/c/github/okfn-brasil/perfil-politico.svg)](https://codecov.io/gh/okfn-brasil/perfil-politico)
[![Code Climate](https://img.shields.io/codeclimate/maintainability/okfn-brasil/perfil-politico.svg)](https://codeclimate.com/github/okfn-brasil/perfil-politico)
[![Apoia.se](https://img.shields.io/badge/donate-apoia.se-EB4A3B.svg)](https://apoia.se/serenata)

# Perfil Político

A platform for profiling candidates in Brazilian 2018 General Election, based
entirely on open data.

## Install

This project requires [Docker](https://docs.docker.com/install/) and
[Docker Compose](https://docs.docker.com/compose/install/).

### Settings

To run the API, you must copy the `.env.sample` to a `.env` file. You can edit
it accordingly if you want run in a production env.

#### Creating the container

You need to create the docker container:

```sh
$ docker-compose up -d
```

#### Database initial setup

You should create your database by applying migrations:

```sh
$ docker-compose run django ./manage.py migrate
```

### Running

To run the project locally, you can simply use this command:

```sh
$ docker-compose up
```

The website and [API](#api) will be available at
[`localhost:8000`](http://localhost:8000) and the Jupyter at
[`localhost:8888`](http://localhost:8888).

### Bringing data into your database

Your local `data/` directory is mapped, inside the container, to `/mnt/data`.
Each command uses a CSV (compressed as `.xz` or not) from a public and
available source. Use `--help` for more info. Yet some extra data can be
generated with some Django custom commands.

Once you have download the datasets to `data/`, you can **create your own database from scratch**
running:

```sh
$ docker-compose run django python manage.py load_affiliations /mnt/data/filiacao.csv
$ docker-compose run django python manage.py update_politicians --ignore_existing_politicians
$ docker-compose run django python manage.py load_candidates /mnt/data/candidatura.csv
$ docker-compose run django python manage.py link_affiliations_and_candidates
$ docker-compose run django python manage.py link_politicians_and_election_results
$ docker-compose run django python manage.py load_assets /mnt/data/bemdeclarado.csv
$ docker-compose run django python manage.py load_bills /mnt/data/senado.csv
$ docker-compose run django python manage.py load_bills /mnt/data/camara.csv
```
> :warning: Note that it will change the primary keys for all politicians in de database!
> So be careful on running it for production environment because some endpoints as
> ` /api/candidate/<pk>/` depends on this primary key to retrieve the correct data.

Or you can **update the data from your database** using the commands:

```sh
$ docker-compose run django python manage.py insert_or_update_affiliations /mnt/data/filiacao.csv
$ docker-compose run django python manage.py update_politicians
$ docker-compose run django python manage.py load_candidates /mnt/data/candidatura.csv --clean-previous-data
$ docker-compose run django python manage.py link_affiliations_and_candidates
$ docker-compose run django python manage.py link_politicians_and_election_results
$ docker-compose run django python manage.py load_assets /mnt/data/bemdeclarado.csv --clean-previous-data
```

> PS: The code only updates data coming from the csv's to the database.
  It does not consider the possibility of changing data that is already on the
  database but does not appear in the csv for some reason (in this case the data
  in the database is kept untouched).

> PS 2: we still don't have commands to update the bills.

### API

#### `GET /api/candidate/<year>/<state>/<post>/`

List all candidates from a certain state to a given post. For example:

`/api/candidate/2018/df/deputado-distrital/`

Post options for 2018 are:

* `1o-suplente`
* `2o-suplente`
* `deputado-distrital`
* `deputado-estadual`
* `deputado-federal`
* `governador`
* `presidente`
* `senador`
* `vice-governador`
* `vice-presidente`

State options are the abbreviation of the 27 Brazilian states, plus `br` for
national election posts.

#### `GET /api/candidate/<pk>/`

Returns the details of a given candidate.

#### `GET /api/stats/<year>/<post>/<characteristic>/`

Get national statistics for a given characteristic in a elected post.

Post options are:

* `deputado-distrital`
* `deputado-estadual`
* `deputado-federal`
* `governador`
* `prefeito`
* `senador`
* `vereador`

Characteristic options are:

* `age`
* `education`
* `ethnicity`
* `gender`
* `marital_status`
* `occupation`
* `party`

#### `GET /api/stats/<state>/<year>/<post>/<characteristic>/`

Same as above but aggregated by state.

## Tests

```sh
$ docker-compose run django py.test
$ docker-compose run django black . --check
```
