# GymHero

Simple application to create training plans, log workouts, add own exercise and many others...


### Motivation
To build an CRUD API with FastAPI, SQLAlchemy, Postgres, Docker



**Initial Data Modeling - Define entities**:
- Exercise 
- ExerciseType 
- Level (Average, Beginner, Intermediate, Advanced)
- BodyPart
- TrainingUnit
- TrainingPlan
- User

**Setup Python Environment**
- Build venv [x]
- Prepare docker-compose with postgres [x]
- Install dependencies (poetry) [x]
- Initialize alembic [x]
- Prepare app configuration (pydantic) [x]

**Write initial ORM and make alembic migration**
- Use SQLAlchemy do define tables [x]

**Define Schemas with Pydantic**
- Use Pydantic to define coresponding object to ORM objects. [x]

**Define dependencies in FastAPI**
- Pagination, Active user, Superuser, Database [x]

**Write initial CRUD for all entities**
- Create, Update, Delete, Read functions [x]

**Add security**:
- Add JWT authentication [x]
- Users module [x]
- Password hashing [x]
- Login endpoint [x]
- Register endpoint [x]

**Add first unit/integration tests**
- pytest []


**Upgrade docker-compose** 
- Define whole app in docker-compose []
- Think about adding Redis for caching requests []


## Define use cases:

### Exercises

| Routes     | Method | Endpoint                 | Access            |
|------------|--------|--------------------------|------------------ |
| /exercises | GET    | /all                     | All               |
| /exercises | GET    | /mine                    | Owner             |
| /exercises | GET    | /{exercise_id}           | All               |
| /exercises | DELETE | /{exercise_id}           | Superuser, Owner  |
| /exercises | PUT    | /{exercise_id}           | Superuser, Owner  |
| /exercises | GET    | /name/{exercise_name}    | All               |
| /exercises | POST   |                          | All               |

### ExerciseType

| Routes          | Method  | Endpoint                 | Access            |
|------------------|--------|--------------------------|-----------        |
| /exercise-types | GET     | /all                     | All               |
| /exercise-types | GET    | /{exercise_type_id}       | All               |
| /exercise-types | DELETE | /{exercise_type_id}       | Superuser         |
| /exercise-types | PUT    | /{exercise_type_id}       | Superuser         |
| /exercise-types | GET    | /name/{exercise_type_name}| All               |
| /exercise-types | POST   |                           | Superuser         |


### Levels

| Routes           | Method | Endpoint         | Access     |
|------------------|--------|------------------|------------|
| /levels          | GET    | /all             | All        |
| /levels          | GET    | /{level_id}      | All        |
| /levels          | DELETE | /{level_id}      | Superuser  |
| /levels          | PUT    | /{level_id}      | Superuser  |
| /levels          | GET    | /name/{level_id} | All        |
| /levels          | POST   |                  | Superuser  |


### Users

