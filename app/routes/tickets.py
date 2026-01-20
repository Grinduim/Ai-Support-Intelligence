from fastapi import APIRouter
from app.models import TicketAnalyzeRequest, TicketAnalyzeResponse
from app.services.risk_analyzer import analyze_ticket

router = APIRouter()

@router.post("/analyze", response_model=TicketAnalyzeResponse)
def analyze_ticket_endpoint(payload: TicketAnalyzeRequest):
    return analyze_ticket(payload)