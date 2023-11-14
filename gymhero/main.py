from fastapi import FastAPI
from gymhero.api.routes.exercise import router as exercise_router

app = FastAPI()

app.include_router(exercise_router, prefix="/exercise", tags=["exercise"])


@app.get("/")
def root():
    return {"message": "Hello world"}
