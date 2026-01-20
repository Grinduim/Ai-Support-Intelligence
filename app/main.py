from fastapi import FastAPI
from app.routes import tickets

app = FastAPI(title="AI Support Intelligence")

app.include_router(tickets.router, prefix="/tickets")

