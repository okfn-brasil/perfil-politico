[![Travis CI](https://img.shields.io/travis/okfn-brasil/perfil-politico.svg)](https://travis-ci.org/okfn-brasil/perfil-politico)
[![Codecov](https://img.shields.io/codecov/c/github/okfn-brasil/perfil-politico.svg)](https://codecov.io/gh/okfn-brasil/perfil-politico)
[![Code Climate](https://img.shields.io/codeclimate/maintainability/okfn-brasil/perfil-politico.svg)](https://codeclimate.com/github/okfn-brasil/perfil-politico)
[![Apoia.se](https://img.shields.io/badge/donate-apoia.se-EB4A3B.svg)](https://apoia.se/serenata)

# Perfil Político

Uma plataforma que apresenta o perfil dos candidatos ao pleito de 2018 nas 
eleições gerais do Brasil, utilizando dados abertos.


## Instalação

Esse projeto requer a instalação do [Docker](https://docs.docker.com/install/) 
e do [Docker Compose](https://docs.docker.com/compose/install/).

### Configuração

Para rodar a API, você precisa copiar o `.env.sample` para um arquivo chamado 
`.env`. Se for utilizar esse projeto em produção, você deve editá-lo de acordo 
com sua necessidade.

### Inicializando os containers para o projeto

Para inicializar, você precisa executar:

```sh
$ docker-compose up -d
```

Além de inicializar processos do docker, este comando também cria alguns 
diretórios e arquivos específicos do projeto. Um deles é o `data/`, que 
será usado mais à frente.


#### Configuração inicial do banco de dados

Para configurar o banco de dados da aplicação, é necessário executar o seguinte 
comando:


```sh
$ docker-compose run django ./manage.py migrate
```

Isto fará com que as tabelas do banco de dados sejam criadas de acordo com o 
modelo definido no Django.


### Executando o projeto


Para iniciar a aplicação, você precisa executar o comando abaixo:

```sh
$ docker-compose up -d
```

O website e a [API](#api) estarão disponíveis em
[`localhost:8000`](http://localhost:8000) e e o Jupyter em
[`localhost:8888`](http://localhost:8888).


#### Inserindo dados

Para ter dados e conseguir usar no seu projeto, você precisa baixá-los 
manualmente dentro do diretório local data/ (criado durante inicialização do 
projeto). Dentro do container docker, a pasta é /mnt/data.

Utilize um arquivo CSV para inserir os dados no banco de dados. 

Utilize --help para mais informações. 

Uma vez que os dados foram baixados e estão armazenados dentro do diretório 
data/, execute os seguintes comandos:

```sh
$ docker-compose run django python manage.py load_affiliations /mnt/data/filiacao.csv
$ docker-compose run django python manage.py load_candidates /mnt/data/candidatura.csv
$ docker-compose run django python manage.py link_affiliations_and_candidates
$ docker-compose run django python manage.py link_politicians_and_election_results
$ docker-compose run django python manage.py load_assets /mnt/data/bemdeclarado.csv
$ docker-compose run django python manage.py load_bills /mnt/data/senado.csv
$ docker-compose run django python manage.py load_bills /mnt/data/camara.csv
```

### API

#### `GET /api/candidate/<year>/<state>/<post>/`

Lista todos os candidados ao pleito de um determinado estado. 

O parâmetro <year> é referente ao ano do pleito.

O parâmetro <state> é relacionado à sigla dos 27 estados brasileiros ou `br` para
eleições nacionais. 

O parâmetro <post> representa qual vaga o candidato está concorrendo. As possíveis
opções são:

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

Por exemplo `/api/candidate/2018/df/deputado-distrital/`.


#### `GET /api/candidate/<pk>/`

Retorna informações detalhadas de um candidato.


#### `GET /api/stats/<year>/<post>/<characteristic>/`

Retorna as estatísticas a níveis nacional do candidado a eleição.

Opções para o parâmetro *post*:

* `deputado-distrital`
* `deputado-estadual`
* `deputado-federal`
* `governador`
* `prefeito`
* `senador`
* `vereador`

Opções para o parâmetro *characteristic*:

* `age`
* `education`
* `ethnicity`
* `gender`
* `marital_status`
* `occupation`
* `party`

#### `GET /api/stats/<state>/<year>/<post>/<characteristic>/`

Similar à rota anterior, porém apresenta as informações organizadas por estado.


## Testes
Para executar os testes e formatação dos scripts modificados

```sh
$ docker-compose run django py.test
$ docker-compose run django black . --check
```
