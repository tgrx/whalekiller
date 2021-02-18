# WhaleKiller

This service provide security checks
for your cloud VMs.

## How to use

RTFM

## How to run locally

### Docker

Use [docker-compose](https://docs.docker.com/compose/).
You **MUST** use one of version 3.3+.

Containers:

1. `whalekiller-web` is running on `8888:80`.
1. `whalekiller-db` is running on `5555:5432`.
   - PostgreSQL 13.1.
   - catalog is on tmpfs volume.
1. `whalekiller-dba` is running on `5556:8080`.

### Bare metal

#### Requirements

1. [Python 3.9](https://www.python.org/)
   **MUST** be available  as `python3` command
   in default system shell. 
1. [Pipenv](https://pipenv.pypa.io/en/latest/)
   **MUST** be available as `pipenv` command 
   in default system shell.
1. [GNU Make](https://www.gnu.org/software/make/)
   **MUST** be available as `make` command
   in default system shell.

#### System setup

A folder [src/](src/) **MUST** be added to `PYTHONPATH`.

This setting is already set in [.env](.env) file.

Pipenv automatically set this up
on `pipenv run` commands.

#### Virtualenv

The command `make venv-dev` will end up
with a `.venv/` folder created.
It will be used as virtualenv location.

Packages to be installed are listed in [Pipfile](Pipfile).

Section `[packages]` contains packages
which are needed for service itself.

Section `[dev-packages]` contains packages
which are needed for development.

All packages are versioned.

You **MAY** set up a virtualenv by your way.

The virtualenv path **MUST** be discoverable
by `pipenv --venv` command.

If not, you **MUST**:
1. update a path to venv in [Makefile.in.mk],
   variable `DIR_VENV`.
1. set `VENV_SYNTHETIC=1`
   in your `config/.secrets.yml` file.

#### Database

The project is built
upon [Postgresql 13.1](https://www.postgresql.org/).

Regardless of your preferred way of installation
the db service **MUST** be available
via the database url
in the following format:
`postgresql://user:pass@host:port/dbname`.

Please see the pre-run actions later.

#### Config

The default configuration is placed 
in [config/settings.yml](config/settings.yml) file.
Everything is already configured.
Normally one does not need to touch
anything in this file.

However, you have to set up your DB.

Hence, you **MUST** create the file
`.secrets.yml` in [config/](config/) folder.
The format is the same as in [config/settings.yml](config/settings.yml).

You **SHOULD** add a `default:` section there
and configure the settings with your values:

```yaml
default:
  DATABASE_URL: "postgresql://username:password@dbhost:dbport/dbname"

  # optional: if you want to run Selenium tests.
  # Choices are "chrome" and "firefox" for now.
  # And you **MUST** have chromedriver or geckodriver
  # installed, respectively.
  TEST_BROWSER: "chrome"
  TEST_BROWSER_HEADLESS: true
```

#### Pre-run actions

You **MUST** create the database.

If

1. commands `createdb` and `dropdb`
   are accessible in your default shell,
1. your PostgreSQL password is visible to them
   ([.pgpass](https://www.postgresql.org/docs/current/libpq-pgpass.html)),

then you **MAY** issue the command `make initdb` 
to do all the stuff.

Else, you have to create the DB in your way.
Then you **MUST** apply the migrations 
by issuing a command `make migrate`.

#### Run

`make run` will run the API server 
on [localhost:8000](http://localhost:8000).

You **MAY** change the port via `PORT` setting
in your `config/.secrets.yml`.

#### Debugging

You **MAY** use [src/main/app.py](src/main/app.py)
as a runner script.
