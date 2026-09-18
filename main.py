from fastapi import FastAPI

from app.routers import (
    games,
    game_sessions,
    game_results,
    auth,
    caregiver,
    daily_task,
    notification
)

app = FastAPI()

app.include_router(games.router)
app.include_router(game_sessions.router)
app.include_router(game_results.router)
app.include_router(auth.router)
app.include_router(caregiver.router)
app.include_router(daily_task.router)
app.include_router(notification.router)


@app.get("/")
def home():
    return {"message": "Memora backend is running!"}