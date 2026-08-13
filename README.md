# GymHero

Simple application to manage your gym training workouts.
You have the flexibility to create your own exercises, you can develop custom training units and these units can be easily integrated into personalized training plans. You can manage your training units by adding or removing exercises as needed.
By default application contains database od more than 1000 exercises.


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
    - mise - toolchain manager (pins Python + uv)
    - uv - dependency management and virtualenvs
    - ruff - linting and formatting
    - mypy - static type checking
    - pre-commit

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
- [mise](https://mise.jdx.dev) — manages Python + uv and runs the project tasks (`mise run <task>`)


clone repository:

```bash
git clone https://github.com/JakubPluta/gymhero.git
```
and navigate to cloned project

build and run project:

```bash
# build image, start containers (detached) and run migrations + db seed
mise run dev
```

alternatively you can use docker commands directly:
```bash

docker compose build
docker compose up -d 
docker exec -it app alembic downgrade base && alembic upgrade head
docker exec -it app python -m scripts.seed --env=dev
```
or 
```bash
docker compose build --no-cache
docker compose up -d --force-recreate
docker exec -it app alembic downgrade base && alembic upgrade head
docker exec -it app python -m scripts.seed --env=dev
```

next time you can just start the stack:
```bash
mise run up
# or directly
docker compose up -d
```

to (re)initialize the db:
```bash
mise run migrate && mise run seed
```

to stop the stack:
```bash
mise run down
```

to run tests (spins a Postgres testcontainer — needs Docker):
```bash
mise run test          # full suite
mise run test-cov      # with coverage
```

to lint / type-check:
```bash
mise run lint          # ruff format --check + ruff check + mypy
mise run lint-fix      # auto-format and fix
```

alembic commands (run inside the app container):

```bash
mise run migrate         # upgrade to head
mise run makemigration   # autogenerate a revision
# or directly:
docker compose exec app alembic upgrade head
docker compose exec app alembic downgrade -1
```

### Configuration
All settings come from `.env.defaults` (committed dummy values). Override any of
them with a git-ignored `.env` or real environment variables. Tests set `ENV=test`
and get their database from a Postgres testcontainer.

`mise run dev` seeds the database and creates the first superuser from those defaults:
```
FIRST_SUPERUSER_USERNAME=admin
FIRST_SUPERUSER_EMAIL=admin@example.com
FIRST_SUPERUSER_PASSWORD=changeme
```
Change them via a local `.env` before running against anything real.

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



#### TODO:
- Add couple of default training plans e.g FBW, PPL, Splits etc - that every registered use can access
- Add environment for local testsing etc.
- Add redis cache
- Improve test fixtures
- Migrate to async 
