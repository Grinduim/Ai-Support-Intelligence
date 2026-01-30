from fastapi import FastAPI
from app.routes import tickets, replies, health

app = FastAPI(title="AI Support Intelligence")

app.include_router(health.router)
app.include_router(tickets.router, prefix="/tickets")
app.include_router(replies.router, prefix="/replies")

