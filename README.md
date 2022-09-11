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
> Note: You can use `docker compose` instead of `docker-compose` in this project.

#### Database initial setup

You should create your database by applying migrations:

```sh
$ docker-compose run --rm django ./manage.py migrate
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
$ docker-compose run --rm django ./manage.py load_affiliations /mnt/data/filiacao.csv
$ docker-compose run --rm django ./manage.py load_candidates /mnt/data/candidatura.csv
$ docker-compose run --rm django ./manage.py link_affiliations_and_candidates
$ docker-compose run --rm django ./manage.py link_politicians_and_election_results
$ docker-compose run --rm django ./manage.py load_assets /mnt/data/bemdeclarado.csv
$ docker-compose run --rm django ./manage.py pre_calculate_stats
$ docker-compose run --rm django ./manage.py load_bills /mnt/data/senado.csv
$ docker-compose run --rm django ./manage.py load_bills /mnt/data/camara.csv
$ docker-compose run --rm django ./manage.py load_income_statements /mnt/data/receita.csv
# make sure to read the instructions on populate_company_info.sql before running the next command
$ docker-compose run --rm postgres psql -U perfilpolitico < populate_company_info.sql
```
> :warning: Note that it will change the primary keys for all candidates in the database!
> So be careful on running it for production environment because some endpoints as
> ` /api/candidate/<pk>/` depends on this primary key to retrieve the correct data.

Or you can **update the data from your database** using the commands:

```sh
$ docker-compose run --rm django ./manage.py unlink_and_delete_politician_references
$ docker-compose run --rm django ./manage.py load_affiliations /mnt/data/filiacao.csv clean-previous-data
$ docker-compose run --rm django ./manage.py update_or_create_candidates /mnt/data/candidatura.csv
$ docker-compose run --rm django ./manage.py link_affiliations_and_candidates
$ docker-compose run --rm django ./manage.py link_politicians_and_election_results
$ docker-compose run --rm django ./manage.py load_assets /mnt/data/bemdeclarado.csv clean-previous-data
$ docker-compose run --rm django ./manage.py pre_calculate_stats
$ docker-compose run --rm django ./manage.py load_bills /mnt/data/senado.csv clean-previous-data
$ docker-compose run --rm django ./manage.py load_bills /mnt/data/camara.csv
```

> Note: The code only updates data coming from the csv's to the database.
  It does not consider the possibility of changing data that is already in the
  database but does not appear in the csv for some reason (in this case the data
  in the database is kept untouched). Commands passing the `clean-previous-data-option` will
  replace all the data for the respective csv, thus changing all primary keys.

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

#### `GET /api/economic-bonds/candidate/<pk>/`

Get electoral income history for a given candidate and companies that have a partnership.

Returns an object with the structure:
```
{
  "companies_associated_with_politician": [
    {
      "cnpj": string,
      "company_name": string,
      "main_cnae": string,
      "secondary_cnaes": string (cnaes separated by ','),
      "uf": string,
      "foundation_date": string (date format 'YYYY/MM/DD'),
      "participation_start_date": string (date format 'YYYY/MM/DD')
    }
    // ... other companies in the same format as above ...
  ],
  "election_income_history": [
    {
      "year": int,
      "value": float,
      "donor_name": string,
      "donor_taxpayer_id": string
      "donor_company_name": string
      "donor_company_cnpj": string
      "donor_economic_sector_code": string,
      "donor_secondary_sector_codes": string
    },
    // ... other income statements in the same format as above ...
  ]
}
```

#### `GET /api/stats/<year>/<post>/<characteristic>/`

Get national statistics for a given characteristic in a elected post.

Post options are:

* `deputado-distrital`
* `deputado-estadual`
* `deputado-federal`
* `governador`
* `prefeito`
* `presidente`
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

#### `GET /api/asset-stats/`

Returns an object with a key called `mediana_patrimonios` that is a list with
the median of elected people's asset value aggregated by year.

`optionally` you can add query parameters to filter the results by `state` or by
the `candidate post` (the valid posts are the same ones that are in the list above).

These parameters can support multiple values if you wish to filter by more than one thing.

Ex: `/api/asset-stats?state=MG&state=RJ&candidate_post=governador&candidate_post=prefeito`

## Tests

```sh
$ docker-compose run --rm django py.test
$ docker-compose run --rm django black . --check
```
