# Medido de Poder

Project is currently developed in Python `3.6.1`

## Dependencies

Add dependencies:

```
$ pip install -r requirements
```

## API

Run the api:

```
$ python api/manage.py runserver
```

To run the api, you must copy the `env-template` to a `.env` file and 
add the url for the MongoDB where the data is stored.

Run api tests:

```
$ cd api
$ pytest 
```
