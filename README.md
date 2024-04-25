# acms-backend
Amalitech Capacity Management System Backend API

### Backend

Backend is a django application running locally at http://localhost:8000

## Developer guide

Local enviroment setup

### Requirements

Install the following dependencies globaly on your system:

- Install [Docker](https://www.docker.com/)
- Install `Make` depending on your OS. [Windows Installation](https://linuxhint.com/install-use-make-windows/), [Ubuntu Installation](https://linuxhint.com/install-make-ubuntu/)

#### local develop

if you are going to contribute, clone the repo.

```.env
$ clone the repo to your local machine `git@github.com:AmaliTech-Training-Rw/acms-backend.git`
```

### How to run the app locally

make a copy of `.env.example` and create a file `env`. Enter the appropriate credentials

- ```env.
    $ cp .env.example .env
  ```
- Reachout to the dev team if unsure about the env vars to use

Run local build

```
$ make build
```

Bring the project up

```
$ make up
```

Run the migrations to create initial django models, celery beat and results models
```sh
make migrate
```

You might already know this, but you may want to create a super user

```.env
make superuser
```

On a browser of your choice go to `http://localhost:8000/`

#### IDE Linting

The container logs will show errors for the backend containers.


### Makefile

Make use of the make commands in the makefile(they just make your dockerized life easier). Be sure to read the Makefile to find out the other tasks that you can make easier

- To build the app, bring up the app, run migrations, add new django apps


### Contributing

- Create your feature branch: git checkout -b `feat/summarized-issue-name`

  > feat/add-a-comma

- Commit your changes: git commit -am `commit message` in past tense

  > Updated settings for holograph projector

- Push to the branch: git push origin `feat/my-new-feature`
- Submit a pull request following the Pull Request template


### Committing your code

- Install pre-commit: `pip install pre-commit`.

- Install black on your machine: `pip install black`

- Install flake on your machine: `pip install flake8`

- Execute `pre-commit install` to install git hooks in your .git/ directory.

Now black can update your python code on committing if there are issues and you can
just go ahead and stage these black changes and you should be good to go.


### Deployment

All our deployments are done by a CI/CD pipeline


### Celery

Make sure you have set the following env vars

- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND

Start a task queue with a worker
> celery -A acms worker -l info

Start a task queue with a dedicated worker
> celery -A acms worker -l info -n worker.low -Q low

To start the celery beat service:
> celery -A acms beat

To start the celery beat service with its worker:
> celery -A acms worker --beat -l info

To specify a schedular, default schedular is `celery.beat.PersistentScheduler` that simply
keeps track of the last run times in a local shelve database file

We use the `django_celery_beat.schedulers:DatabaseScheduler` that stores schedules in the DB and also allows
scheduling via Django-Admin
> celery -A acms beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

#### Queues

- We have 3 queues
    - low
    - celery  # default
    - high

#### Task routes

All messages are sent to the Exchange that routes them to queues using the task routing rules defined.

Tasks without priority queues default to the celery queue. Each queue has a dedicated worker.

Task results are stored in rabbitmq as the backend. Task execution results are ignored by default.

To store a result in rabbitmq, override at task level e.g.
```py
@app.task(ignore_result=False)
def store_result():
    logger.info(f'storing result. check rabbitmq instance')
    return 'result'
```

##### Logging inside tasks

Use the celery logger as it can access result values during execution unlike the python logger
```py
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
logger.info('adding')

```
