from fastapi import FastAPI

from gymhero.api import (
    auth_router,
    bodypart_router,
    exercise_router,
    exercise_type_router,
    level_router,
    training_plan_router,
    training_unit_router,
    user_router,
)

app = FastAPI(title="GymHero API", version="0.1.0")

app.include_router(exercise_router, prefix="/exercises", tags=["exercise"])
app.include_router(
    exercise_type_router, prefix="/exercise-types", tags=["exercise_types"]
)
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(level_router, prefix="/levels", tags=["levels"])
app.include_router(bodypart_router, prefix="/body-parts", tags=["bodyparts"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(
    training_plan_router, prefix="/training-plans", tags=["training_plans"]
)
app.include_router(
    training_unit_router, prefix="/training-units", tags=["training_units"]
)


@app.get("/")
def root():
    return {"message": "Hello world"}
