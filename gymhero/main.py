from fastapi import FastAPI
from gymhero.api.routes.exercise import router as exercise_router
from gymhero.api.routes.user import router as user_router
from gymhero.api.routes.level import router as level_router
from gymhero.api.routes.bodypart import router as bodypart_router

app = FastAPI()

app.include_router(exercise_router, prefix="/exercise", tags=["exercise"])
app.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(level_router, prefix="/level", tags=["level"])
app.include_router(bodypart_router, prefix="/bodypart", tags=["bodypart"])


@app.get("/")
def root():
    return {"message": "Hello world"}
