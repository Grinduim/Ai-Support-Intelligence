from app.models import Ticket, TicketResult
from app.services.risk_analyzer import analyze_ticket as analyze_heuristic
from app.services.llm_engine import analyze_with_llm

MIN_CONFIDENCE = 55

async def analyze_one_ticket(ticket: Ticket) -> TicketResult:
    baseline_resp = analyze_heuristic(ticket)
    baseline = baseline_resp
    
    try:
        ai = await analyze_with_llm(ticket)
        #guardrail: do not let the lmm get  down the score with critical sinal
        if ai.confidence >= MIN_CONFIDENCE:
            if "escaltion" in " ".join(baseline.debug_signals) and baseline.risk_label == "HIGH": 
                return baseline
        
        return TicketResult(
                id=ticket.id,
                risk_score=ai.risk_score,
                risk_label=ai.risk_label,
                reason=ai.reason,
                suggested_action=ai.suggested_action,
                risk_breakdown=baseline.risk_breakdown,   # mantém breakdown heurístico por enquanto
                debug_signals=baseline.debug_signals + [f"llm_confidence:{ai.confidence}"] + [f"llm_signal:{s}" for s in ai.signals],
            )
        
    except Exception as e:
        baseline.debug_signals.append(f"llm_error:{type(e).__name__}")
        
    return baseline