import pytest
from pydantic import ValidationError
from app.models import (
    Ticket, TicketAnalyzeRequest, TicketResult, RiskLabel,
    AIAnalysis, ReplySuggestionRequest, ReplySuggestionResponse
)


class TestTicketModel:
    """Test Ticket model validation."""
    
    def test_ticket_valid(self):
        """Test valid ticket creation."""
        ticket = Ticket(
            id="TICKET-001",
            customer="John Doe",
            channel="email",
            last_message="Hello support",
            conversation_summary="Initial contact",
            sla_hours_open=5,
            language="en-US"
        )
        assert ticket.id == "TICKET-001"
        assert ticket.customer == "John Doe"
        assert ticket.language == "en-US"
    
    def test_ticket_last_message_max_length(self):
        """Test last_message exceeds max length (255 chars)."""
        with pytest.raises(ValidationError) as exc_info:
            Ticket(
                id="TICKET-001",
                customer="John Doe",
                channel="email",
                last_message="x" * 256,  # 256 chars, exceeds limit
                conversation_summary="Valid",
                sla_hours_open=5
            )
        assert "should have at most 255 characters" in str(exc_info.value).lower()
    
    def test_ticket_conversation_summary_max_length(self):
        """Test conversation_summary exceeds max length (255 chars)."""
        with pytest.raises(ValidationError) as exc_info:
            Ticket(
                id="TICKET-001",
                customer="John Doe",
                channel="email",
                last_message="Valid",
                conversation_summary="x" * 256,  # 256 chars, exceeds limit
                sla_hours_open=5
            )
        assert "should have at most 255 characters" in str(exc_info.value).lower()
    
    def test_ticket_language_default(self):
        """Test default language is en-US."""
        ticket = Ticket(
            id="TICKET-001",
            customer="John Doe",
            channel="email",
            last_message="Hello",
            conversation_summary="Summary",
            sla_hours_open=5
        )
        assert ticket.language == "en-US"
    
    def test_ticket_exactly_255_chars_allowed(self):
        """Test exactly 255 characters is allowed."""
        ticket = Ticket(
            id="TICKET-001",
            customer="John Doe",
            channel="email",
            last_message="x" * 255,
            conversation_summary="y" * 255,
            sla_hours_open=5
        )
        assert len(ticket.last_message) == 255
        assert len(ticket.conversation_summary) == 255


class TestRiskLabelEnum:
    """Test RiskLabel enum."""
    
    def test_risk_labels(self):
        """Test all risk label values."""
        assert RiskLabel.LOW == "LOW"
        assert RiskLabel.MEDIUM == "MEDIUM"
        assert RiskLabel.HIGH == "HIGH"


class TestTicketAnalyzeRequest:
    """Test TicketAnalyzeRequest model."""
    
    def test_analyze_request_single_ticket(self):
        """Test request with single ticket."""
        ticket = Ticket(
            id="TICKET-001",
            customer="John Doe",
            channel="email",
            last_message="Help me",
            conversation_summary="Need assistance",
            sla_hours_open=5
        )
        request = TicketAnalyzeRequest(tickets=[ticket])
        assert len(request.tickets) == 1
        assert request.tickets[0].id == "TICKET-001"
    
    def test_analyze_request_multiple_tickets(self):
        """Test request with multiple tickets."""
        tickets = [
            Ticket(
                id=f"TICKET-{i:03d}",
                customer=f"Customer {i}",
                channel="email",
                last_message=f"Message {i}",
                conversation_summary=f"Summary {i}",
                sla_hours_open=i
            )
            for i in range(1, 6)
        ]
        request = TicketAnalyzeRequest(tickets=tickets)
        assert len(request.tickets) == 5


class TestTicketResult:
    """Test TicketResult model."""
    
    def test_ticket_result_valid(self):
        """Test valid ticket result."""
        result = TicketResult(
            id="TICKET-001",
            risk_score=75,
            risk_label=RiskLabel.HIGH,
            reason="Customer escalated",
            suggested_action="Contact senior support",
            debug_signals=["escalation: procon"],
            risk_breakdown={"escalation": 40, "churn": 0, "sla": 35, "sentiment": 0},
            language="en-US"
        )
        assert result.id == "TICKET-001"
        assert result.risk_score == 75
        assert result.risk_label == RiskLabel.HIGH


class TestAIAnalysis:
    """Test AIAnalysis model."""
    
    def test_ai_analysis_valid(self):
        """Test valid AI analysis."""
        analysis = AIAnalysis(
            risk_score=80,
            risk_label=RiskLabel.HIGH,
            reason="Escalation threat detected",
            suggested_action="Escalate immediately",
            confidence=92,
            signals=["escalation", "sla_aging"]
        )
        assert analysis.risk_score == 80
        assert analysis.confidence == 92
    
    def test_ai_analysis_confidence_bounds(self):
        """Test confidence must be 0-100."""
        # Test confidence above 100
        with pytest.raises(ValidationError) as exc_info:
            AIAnalysis(
                risk_score=50,
                risk_label=RiskLabel.MEDIUM,
                reason="Test",
                suggested_action="Test",
                confidence=101  # Invalid: > 100
            )
        assert "less than or equal to 100" in str(exc_info.value).lower()
        
        # Test negative confidence
        with pytest.raises(ValidationError) as exc_info:
            AIAnalysis(
                risk_score=50,
                risk_label=RiskLabel.MEDIUM,
                reason="Test",
                suggested_action="Test",
                confidence=-1  # Invalid: < 0
            )
        assert "greater than or equal to 0" in str(exc_info.value).lower()
    
    def test_ai_analysis_confidence_boundaries(self):
        """Test confidence at boundaries (0 and 100)."""
        analysis_0 = AIAnalysis(
            risk_score=0,
            risk_label=RiskLabel.LOW,
            reason="Test",
            suggested_action="Test",
            confidence=0
        )
        assert analysis_0.confidence == 0
        
        analysis_100 = AIAnalysis(
            risk_score=100,
            risk_label=RiskLabel.HIGH,
            reason="Test",
            suggested_action="Test",
            confidence=100
        )
        assert analysis_100.confidence == 100


class TestReplySuggestionRequest:
    """Test ReplySuggestionRequest model."""
    
    def test_reply_suggestion_request_valid(self):
        """Test valid reply suggestion request."""
        request = ReplySuggestionRequest(
            ticket_id="TICKET-001",
            customer="John Doe",
            channel="email",
            last_message="Help!",
            conversation_summary="Customer needs help",
            risk_label=RiskLabel.HIGH,
            company_tone="friendly",
            language="en-US"
        )
        assert request.ticket_id == "TICKET-001"
        assert request.company_tone == "friendly"
    
    def test_reply_suggestion_request_max_length(self):
        """Test message length limits."""
        with pytest.raises(ValidationError):
            ReplySuggestionRequest(
                ticket_id="TICKET-001",
                customer="John Doe",
                channel="email",
                last_message="x" * 256,  # Exceeds 255
                conversation_summary="Valid",
                risk_label=RiskLabel.HIGH,
                company_tone="friendly",
                language="en-US"
            )


class TestReplySuggestionResponse:
    """Test ReplySuggestionResponse model."""
    
    def test_reply_suggestion_response_valid(self):
        """Test valid reply suggestion response."""
        response = ReplySuggestionResponse(
            ticket_id="TICKET-001",
            suggested_reply="Thank you for contacting us...",
            confidence=85,
            language="en-US",
            subject="We're here to help",
            next_steps=["Follow up within 2 hours"],
            do_not_say=["We can't help"]
        )
        assert response.confidence == 85
        assert response.language == "en-US"
    
    def test_reply_suggestion_response_confidence_invalid(self):
        """Test confidence validation in response."""
        with pytest.raises(ValidationError):
            ReplySuggestionResponse(
                ticket_id="TICKET-001",
                suggested_reply="Reply",
                confidence=150,  # Invalid: > 100
                language="en-US"
            )
    
    def test_reply_suggestion_response_defaults(self):
        """Test default values."""
        response = ReplySuggestionResponse(
            ticket_id="TICKET-001",
            suggested_reply="Reply",
            confidence=50
        )
        assert response.language == "en-US"
        assert response.subject == ""
        assert response.next_steps == []
        assert response.do_not_say == []
