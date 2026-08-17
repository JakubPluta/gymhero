# GymHero

Simple application to manage your gym training workouts.
You have the flexibility to create your own exercises, you can develop custom training units and these units can be easily integrated into personalized training plans. You can manage your training units by adding or removing exercises as needed.
By default application contains database of more than 1000 exercises.

### Frontend

A modern SPA (Vite + React + TypeScript, Tailwind + shadcn/ui, TanStack Router/Query)
lives in [`frontend/`](./frontend). It is fully type-safe against this API's OpenAPI
schema. See [`frontend/README.md`](./frontend/README.md) for setup — in short:
`mise run dev` (backend on :8000), then `cd frontend && npm install && npm run gen:api && npm run dev`.


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

```mermaid
erDiagram
    users          ||--o{ exercises                   : creates
    users          ||--o{ training_units              : creates
    users          ||--o{ training_plans              : creates

    body_parts     ||--o{ exercises                   : targets
    exercise_types ||--o{ exercises                   : types
    levels         ||--o{ exercises                   : rates

    training_units ||--o{ training_unit_exercise      : has
    exercises      ||--o{ training_unit_exercise      : in

    training_plans ||--o{ training_plan_training_unit : has
    training_units ||--o{ training_plan_training_unit : in

    users {
        int      id              PK
        string   email           UK
        string   full_name
        string   hashed_password
        bool     is_active
        bool     is_superuser
        int      token_version
        datetime created_at
        datetime updated_at
    }
    exercises {
        int      id                  PK
        string   name                UK
        string   description
        int      target_body_part_id FK
        int      exercise_type_id    FK
        int      level_id            FK
        int      owner_id            FK
        datetime created_at
        datetime updated_at
    }
    exercise_types {
        int      id         PK
        string   name       UK
        datetime created_at
        datetime updated_at
    }
    levels {
        int      id         PK
        string   name       UK
        datetime created_at
        datetime updated_at
    }
    body_parts {
        int      id         PK
        string   name       UK
        datetime created_at
        datetime updated_at
    }
    training_units {
        int      id          PK
        string   name        "unique per owner"
        string   description
        int      owner_id    FK
        datetime created_at
        datetime updated_at
    }
    training_plans {
        int      id          PK
        string   name        "unique per owner"
        string   description
        int      owner_id    FK
        datetime created_at
        datetime updated_at
    }
    training_unit_exercise {
        int training_unit_id PK, FK
        int exercise_id      PK, FK
    }
    training_plan_training_unit {
        int training_plan_id PK, FK
        int training_unit_id PK, FK
    }
```

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
- Separate database and env for testing



## Define use cases:

> All API routes are served under the **`/api/v1`** prefix — e.g. `GET /api/v1/exercises/all`.
> (`/health`, `/ready` and the Swagger docs at `/docs` are not prefixed.)

### Exercises

| Routes     | Method | Endpoint                 | Access                 |
|------------|--------|--------------------------|------------------------|
| /exercises | GET    | /all                     | Active User            |
| /exercises | GET    | /my                      | Owner                  |
| /exercises | GET    | /{exercise_id}           | Active User            |
| /exercises | DELETE | /{exercise_id}           | Superuser, Owner       |
| /exercises | PATCH  | /{exercise_id}           | Superuser, Owner       |
| /exercises | GET    | /name/{exercise_name}    | Active User            |
| /exercises | POST   |                          | Active User            |

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
| /auth          | POST    | /refresh           | All          |
| /auth          | POST    | /logout            | Active User  |


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
| /training-plans  | PUT     | /{training_plan_id}/training-units/{training_unit_id}         | Owner, Superuser  |
| /training-plans  | DELETE  | /{training_plan_id}/training-units/{training_unit_id}         | Owner, Superuser  |


### Training Units

| Routes           | Method  | Endpoint                                            | Access            |
|------------------|---------|-----------------------------------------------------|-------------------|
| /training-units  | GET     | /all                                                | Superuser         |
| /training-units  | GET     | /all/my                                             | Owner, Superuser  |
| /training-units  | GET     | /{training_unit_id}                                 | Owner, Superuser  |
| /training-units  | GET     | /name/{training_unit_name}                          | Owner, Superuser  |
| /training-units  | GET     | /{training_unit_id}/exercises                       | Owner, Superuser  |
| /training-units  | DELETE  | /{training_unit_id}                                 | Owner, Superuser  |
| /training-units  | PUT     | /{training_unit_id}                                 | Owner, Superuser  |
| /training-units  | POST    |                                                     | Owner, Superuser  |
| /training-units  | PUT     | /{training_unit_id}/exercises/{exercise_id}         | Owner, Superuser  |
| /training-units  | DELETE  | /{training_unit_id}/exercises/{exercise_id}         | Owner, Superuser  |



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
docker compose exec app alembic upgrade head
docker compose exec app python -m scripts.seed --env=dev
```
or 
```bash
docker compose build --no-cache
docker compose up -d --force-recreate
docker compose exec app alembic upgrade head
docker compose exec app python -m scripts.seed --env=dev
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
  'http://localhost:8000/api/v1/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=&username=admin%40example.com&password=changeme&scope=&client_id=&client_secret='
```
In response you will receive something like this:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ...",
  "token_type": "bearer"
}
```
And you need to use it in headers when calling other endpoints eg:
```bash
curl -X 'GET' \
  'http://localhost:8000/api/v1/exercises/my?skip=0&limit=10' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDMzMzY5MDYsInN1YiI6IjEifQ.mnbKswazYV8pBv5JWlHv-qJ8fHZ4msW6yWwvRWzKUz4'
```

To register new user (it will be normal user not superuser, so some routes won't be available)
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "mynewuser@mail.com",
  "password": "mypassword",
  "full_name": "My User"
}'
```

You can also do everything by using fast api docs which are more user friendly and more convenient way to play with api. To do that check http://localhost:8000/docs (your app needs to run)



## Possible future work
- Default training plans (FBW / PPL / Split) seeded for every user
- Redis cache for the exercise catalog
