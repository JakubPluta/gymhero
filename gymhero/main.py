from fastapi import FastAPI

from gymhero.api import (
    auth_router,
    bodypart_router,
    exercise_router,
    exercise_type_router,
    level_router,
    user_router,
)

app = FastAPI(title="GymHero API", version="0.1.0")

app.include_router(exercise_router, prefix="/exercise", tags=["exercise"])
app.include_router(exercise_type_router, prefix="/exercise", tags=["exercise_types"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(level_router, prefix="/level", tags=["level"])
app.include_router(bodypart_router, prefix="/bodypart", tags=["bodypart"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/")
def root():
    return {"message": "Hello world"}
