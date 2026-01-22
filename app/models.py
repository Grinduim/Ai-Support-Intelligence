from pydantic import BaseModel
from typing import Dict, List

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
    debug_signals: List[str]
    risk_breakdown: Dict[str, int]

class TicketAnalyzeResponse(BaseModel):
    results: List[TicketResult]
    

class AIAnalysis(BaseModel):
    risk_score: int
    risk_label: str  # LOW | MEDIUM | HIGH
    reason: str
    suggested_action: str
    confidence: int  # 0..100
    signals: List[str] = []