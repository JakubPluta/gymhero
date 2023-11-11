# GymHero

Simple application to create training plans, log workouts, add own exercise and many others...


### Motivation
To build an CRUD API with FastAPI, SQLAlchemy, Postgres, Docker

### Steps

##### Initial Data Modeling - Define entities:
- Exercise
- MuscleGroup
- TrainingUnit
- TrainingPlan
- User

#### Setup Python Environment
- Build venv
- Prepare docker-compose with postgres
- Install dependencies (poetry)
- Initialize alembic
- Prepare app configuration (pydantic)

#### Write initial ORM and make alembic migration
- Use SQLAlchemy do define tables

#### Define Schemas with Pydantic

#### Define dependencies in FastAPI (Depends(get_db))

#### Write initial CRUD for all entities
- Create, Update, Delete, Read functions - no without security

#### Add first unit/integration tests
- pytest

#### Add routes
#### Add users module 
#### Add JWT authentication
#### Upgrade docker-compose
- To keep app in container
