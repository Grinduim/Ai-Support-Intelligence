from fastapi import APIRouter
from app.models import TicketAnalyzeRequest, TicketAnalyzeResponse
from app.services.risk_orchestrator import analyze_one_ticket

router = APIRouter()

@router.post("/analyze", response_model=TicketAnalyzeResponse)
async def analyze_ticket_endpoint(payload: TicketAnalyzeRequest):
    results = []
    for t in payload.tickets:
        results.append(await analyze_one_ticket(t))
    return TicketAnalyzeResponse(results=results)