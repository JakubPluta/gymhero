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
- pytest [x]


**Upgrade docker-compose** 
- Define whole app in docker-compose [x]



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



### Hidden endpoints for superuser

| Routes           | Method  | Endpoint                                            | Access     |
|------------------|---------|-----------------------------------------------------|------------|
| /training-units  | GET     | /name/{training_unit_name}/superuser                | Superuser  |
| /training-plans  | GET     | /name/{training_plan_name}/superuser                | Superuser  |