from pydantic import BaseModel
from typing import List

class Ticket(BaseModel):
    id: str
    customer: str
    channel: str
    last_message: str
    conversation_summary: str
    sla_hours_open: int
    
class TicketAnalyzeRequest(BaseModel):
    tickets: List[Ticket]

class TicketResult(BaseModel):
    id: str
    risk_score: int
    risk_label: str
    reason: str
    suggested_action: str

class TicketAnalyzeResponse(BaseModel):
    results: List[TicketResult]