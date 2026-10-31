from fastapi import FastAPI
from app.routers.notes import router

app = FastAPI(title="Notes API")
app.include_router(router)