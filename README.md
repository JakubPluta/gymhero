# GymHero

Simple application to create training plans, workouts, add own exercise and many others....


### Motivation
To build an CRUD API with FastAPI, SQLAlchemy, Postgres, Docker


#### Data Models
- Exercise 
- ExerciseType 
- Level
- BodyPart
- TrainingUnit
- TrainingPlan
- User

**Entity Relationship Diagram**

![ER Diagram](media/ermodel.png?raw=true "ER Diagram")

#### Core technologies
- FastAPI - web framework for building APIs with Python 3.8+ based on standard Python type hints.
- SQLAlchemy - Object Relational Mapper
- Pydantic -  Data validation library for Python and FastAPI models
- Uvicorn - ASGI web server implementation for Python
- Alembic - lightweight database migration tool for usage with the SQLAlchemy Database Toolkit for Python.
- Docker - tool to package and run an application in a loosely isolated environment
- Docker Compose - tool for defining and running multi-container Docker applications
- Postgres - open source object-relational database
- For testing:
    - pytest
    - pytest-cov
    - pytest-mock
- For development
    - precommit-hook
    - pylint
    - black
    - ruff
    - poetry
    - venv

### Implemented functionalities
- JWT Authentication
- Password Hashing
- Login & Register Endpoints
- ORM Objects representing SQL tables and relationships
- Pydantic schemas
- CRUD module for reading, updating, deleting objects in/from database 
- Pagination
- Dependencies - superuser, active user, database
- Initialization scripts
- Seperate database and env for testing



## Define use cases:

### Exercises

| Routes     | Method | Endpoint                 | Access                 |
|------------|--------|--------------------------|------------------------|
| /exercises | GET    | /all                     | All                    |
| /exercises | GET    | /my                      | Owner                  |
| /exercises | GET    | /{exercise_id}           | All                    |
| /exercises | DELETE | /{exercise_id}           | Superuser, Owner       |
| /exercises | PUT    | /{exercise_id}           | Superuser, Owner       |
| /exercises | GET    | /name/{exercise_name}    | All                    |
| /exercises | POST   |                          | Superuser, Active User |

### ExerciseType

| Routes          | Method  | Endpoint                  | Access                 |
|------------------|--------|---------------------------|------------------------|
| /exercise-types | GET     | /all                      | All                    |
| /exercise-types | GET     | /{exercise_type_id}       | All                    |
| /exercise-types | DELETE  | /{exercise_type_id}       | Superuser              |
| /exercise-types | PUT     | /{exercise_type_id}       | Superuser              |
| /exercise-types | GET     | /name/{exercise_type_name}| All                    |
| /exercise-types | POST    |                           | Superuser              |


### Levels

| Routes           | Method | Endpoint           | Access     |
|------------------|--------|--------------------|------------|
| /levels          | GET    | /all               | All        |
| /levels          | GET    | /{level_id}        | All        |
| /levels          | DELETE | /{level_id}        | Superuser  |
| /levels          | PUT    | /{level_id}        | Superuser  |
| /levels          | GET    | /name/{level_name} | All        |
| /levels          | POST   |                    | Superuser  |


### Body Parts
| Routes           | Method | Endpoint              | Access     |
|------------------|--------|-----------------------|------------|
| /body-parts      | GET    | /all                  | All        |
| /body-parts      | GET    | /{bodypart_id}        | All        |
| /body-parts      | DELETE | /{bodypart_id}        | Superuser  |
| /body-parts      | PUT    | /{bodypart_id}        | Superuser  |
| /body-parts      | GET    | /name/{bodypart_name} | All        |
| /body-parts      | POST   |                       | Superuser  |

### Users


| Routes          | Method | Endpoint           | Access     |
|-----------------|--------|--------------------|------------|
| /users          | GET    | /all               | Superuser  |
| /users          | GET    | /{user_id}         | Superuser  |
| /users          | DELETE | /{user_id}         | Superuser  |
| /users          | PUT    | /{user_id}         | Superuser  |
| /users          | GET    | /email/{email}     | Superuser  |
| /users          | POST   |                    | Superuser  |


### Auth
| Routes         | Method  | Endpoint           | Access     |
|----------------|---------|--------------------|------------|
| /auth          | POST    | /login             | All        |
| /auth          | POST    | /register          | All        |


### Training Plans

| Routes           | Method  | Endpoint                                                      | Access            |
|------------------|---------|----------------------------------------------------------------|------------------|
| /training-plans  | GET     | /all                                                          | Superuser         |
| /training-plans  | GET     | /all/my                                                       | Owner, Superuser  |
| /training-plans  | GET     | /{training_plan_id}                                           | Owner, Superuser  |
| /training-plans  | GET     | /name/{training_plan_name}                                    | Owner, Superuser  |
| /training-plans  | GET     | /{training_plan_id}/training-units                            | Owner, Superuser  |
| /training-plans  | DELETE  | /{training_plan_id}                                           | Owner, Superuser  |
| /training-plans  | PUT     | /{training_plan_id}                                           | Owner, Superuser  |
| /training-plans  | POST    |                                                               | Owner, Superuser  |
| /training-plans  | PUT     | /{training_plan_id}/training-units/{training_unit_id}/add     | Owner, Superuser  |
| /training-plans  | PUT     | /{training_plan_id}/training-units/{training_unit_id}/remove  | Owner, Superuser  |


### Training Units

| Routes           | Method  | Endpoint                                            | Access            |
|------------------|---------|-----------------------------------------------------|-------------------|
| /training-units  | GET     | /all                                                | Superuser         |
| /training-units  | GET     | /all/my                                             | Owner, Superuser  |
| /training-units  | GET     | /{training_unit_id}                                 | Owner, Superuser  |
| /training-units  | GET     | /name/{training_unit_name}                          | Owner, Superuser  |
| /training-units  | GET     | /{training_plan_id}/exercises                       | Owner, Superuser  |
| /training-units  | DELETE  | /{training_plan_id}                                 | Owner, Superuser  |
| /training-units  | PUT     | /{training_plan_id}                                 | Owner, Superuser  |
| /training-units  | POST    |                                                     | Owner, Superuser  |
| /training-units  | PUT     | /{training_unit_id}/exercises/{exercise_id}/add     | Owner, Superuser  |
| /training-units  | PUT     | /{training_unit_id}/exercises/{exercise_id}/remove  | Owner, Superuser  |



### Private superuser endpoints

| Routes           | Method  | Endpoint                                            | Access     |
|------------------|---------|-----------------------------------------------------|------------|
| /training-units  | GET     | /name/{training_unit_name}/superuser                | Superuser  |
| /training-plans  | GET     | /name/{training_plan_name}/superuser                | Superuser  |



## How to run

### You should have
- Running Docker
- Installed Make (not mandatory) - use makefile to run all commands


clone repository:

```bash
git clone https://github.com/JakubPluta/gymhero.git
```
and navigate to cloned project

build and run project:

```bash
# this command will build docker image, up container in detached mode and run db initialization scripts
make dev
```

you can also re-build container 
```bash
make install
```

alternatively if you don't have make installed you can use directly docker commands:
```bash

docker compose build
docker compose up -d 
docker exec -it app alembic downgrade base && alembic upgrade head
docker exec -it app python -m scripts.initdb --env=dev
```
or 
```bash
docker compose build --no-cache
docker compose up -d --force-recreate
docker exec -it app alembic downgrade base && alembic upgrade head
docker exec -it app python -m scripts.initdb --env=dev
```

next time if you already have build container you can just type:
```bash
make up
# or if you did some changes in code
make run
```

alternatively:
```bash
docker compose up -d
# or
docker compose build
docker compose up -d
```

to initialize db once more run:
```bash
make initdb

# or 
docker exec -it app alembic downgrade base && alembic upgrade head
docker exec -it app python -m scripts.initdb --env=dev
```

to down or kill containers:
```bash
make down
# or
make kill
```

to run tests:
```bash
# to run all test
make test-all
# to run all test in vervose mode
make test-all-verboose
# unit tests
make test-unit
# integration test
make test-integration
# run coverage report
make cov
```

alternatively:

```bash
docker exec -it --env-file .env.test app pytest tests/
docker exec -it --env-file .env.test app pytest tests/ -s -vv
docker exec -it --env-file .env.test app pytest --cov=gymhero tests/ 
```

alembic commands:

```bash
# downgrade to base revisions
make alembic-base
# upgrade to head revisions
make alembic-head
# up + 1
make alembic-up
# down -1
make alembic-down
# generate migration
make alembic-migrate
# downgrade base & upgrade head
make alembic-recreate
# downgrade base & upgrade head & and run init db scripts
make alembic-init
```

### Main configuration is located in files:
- env.dev - dev environemnt in container
- env.test - testing environment
- env.local - alternative to run app locally (you need to create venv and install all dependencies)

If you run `make install` or `make dev` or `make run` command then by default database will be initialized with data and first superuser will be created:
```
FIRST_SUPERUSER_USERNAME=gymhero
FIRST_SUPERUSER_EMAIL=gymhero@mail.com
FIRST_SUPERUSER_PASSWORD=gymhero
```
Feel free to change it after cloning repository.

So as you first user is created and app is running you need to generate JWT Token to access different endpoints. To do that use:
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=gymhero%40mail.com&password=gymhero&scope=&client_id=&client_secret='
```
In response you will receive something like this:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDMzMzY3ODgsInN1YiI6IjEifQ.KXtcf8KziA50-xdwe0Fx6fjOFVeaSePp9B6h4EPUwno",
  "token_type": "bearer"
}
```
And you need to use it in headers when calling other endpoints eg:
```bash
curl -X 'GET' \
  'http://localhost:8000/exercises/my?skip=0&limit=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDMzMzY5MDYsInN1YiI6IjEifQ.mnbKswazYV8pBv5JWlHv-qJ8fHZ4msW6yWwvRWzKUz4'
```

To register new user (it will be normal user not superuser, so some routes won't be available)
```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "mynewuser@mail.com",
  "password": "mypassword",
  "full_name": "My User"
}'
```

You can also do everything by using fast api docs which are more user friendly and more convinient way to play with api. To do that check http://localhost:8000/docs (you app needs to run)
