import pytest
from app.services.risk_analyzer import analyze_ticket
from app.models import Ticket, RiskLabel


class TestRiskAnalyzer:
    """Test heuristic risk analyzer."""
    
    def test_analyze_low_risk_ticket(self, sample_ticket_low_risk):
        """Test low risk ticket analysis."""
        result = analyze_ticket(sample_ticket_low_risk)
        assert result.risk_label == RiskLabel.LOW
        assert result.risk_score < 35
        assert "standard response" in result.suggested_action.lower()
    
    def test_analyze_high_risk_escalation(self, sample_ticket_high_risk):
        """Test high risk ticket with escalation signals."""
        result = analyze_ticket(sample_ticket_high_risk)
        assert result.risk_label == RiskLabel.HIGH
        assert result.risk_score >= 70
        assert "escalate" in result.suggested_action.lower()
        assert any("escalation" in sig.lower() for sig in result.debug_signals)
    
    def test_analyze_medium_risk_sla(self, sample_ticket_medium_risk):
        """Test medium risk ticket due to SLA aging."""
        result = analyze_ticket(sample_ticket_medium_risk)
        assert result.risk_label == RiskLabel.MEDIUM
        assert result.risk_score >= 35
        assert result.risk_score < 70
        assert any("sla" in sig.lower() for sig in result.debug_signals)
    
    def test_analyze_churn_signal(self, sample_ticket_churn):
        """Test ticket with churn signals."""
        result = analyze_ticket(sample_ticket_churn)
        assert result.risk_label == RiskLabel.MEDIUM or result.risk_label == RiskLabel.HIGH
        assert any("churn" in sig.lower() for sig in result.debug_signals)
    
    def test_risk_breakdown_structure(self, sample_ticket_high_risk):
        """Test risk breakdown has correct structure."""
        result = analyze_ticket(sample_ticket_high_risk)
        assert "escalation" in result.risk_breakdown
        assert "churn" in result.risk_breakdown
        assert "sla" in result.risk_breakdown
        assert "sentiment" in result.risk_breakdown
        assert all(isinstance(v, int) for v in result.risk_breakdown.values())
    
    def test_risk_score_bounded(self, sample_ticket_high_risk):
        """Test risk score is bounded 0-100."""
        result = analyze_ticket(sample_ticket_high_risk)
        assert 0 <= result.risk_score <= 100
    
    def test_sla_scoring_12h(self):
        """Test SLA scoring at 12 hour threshold."""
        ticket = Ticket(
            id="TEST-1",
            customer="Test",
            channel="email",
            last_message="Help",
            conversation_summary="Summary",
            sla_hours_open=12
        )
        result = analyze_ticket(ticket)
        assert result.risk_breakdown["sla"] == 15
    
    def test_sla_scoring_24h(self):
        """Test SLA scoring at 24 hour threshold."""
        ticket = Ticket(
            id="TEST-1",
            customer="Test",
            channel="email",
            last_message="Help",
            conversation_summary="Summary",
            sla_hours_open=24
        )
        result = analyze_ticket(ticket)
        assert result.risk_breakdown["sla"] == 25
    
    def test_sla_scoring_48h(self):
        """Test SLA scoring at 48 hour threshold."""
        ticket = Ticket(
            id="TEST-1",
            customer="Test",
            channel="email",
            last_message="Help",
            conversation_summary="Summary",
            sla_hours_open=48
        )
        result = analyze_ticket(ticket)
        assert result.risk_breakdown["sla"] == 35
    
    def test_multiple_keywords_accumulate(self):
        """Test that multiple risk signals accumulate."""
        ticket = Ticket(
            id="TEST-1",
            customer="Test",
            channel="email",
            last_message="I want to cancel and I will contact procon about this ridiculous service",
            conversation_summary="Multiple complaints, very negative",
            sla_hours_open=50
        )
        result = analyze_ticket(ticket)
        assert result.risk_label == RiskLabel.HIGH
        assert len(result.debug_signals) > 0
        # Should have escalation, churn, sentiment, and sla signals
    
    def test_ticket_language_not_preserved(self, sample_ticket_churn):
        """Test language isn't preserved in result."""
        result = analyze_ticket(sample_ticket_churn)
        assert result.language != sample_ticket_churn.language
    
    def test_reason_formatting(self, sample_ticket_high_risk):
        """Test reason field is properly formatted."""
        result = analyze_ticket(sample_ticket_high_risk)
        assert result.reason.endswith(".")
        assert len(result.reason) > 0
    
    def test_no_risk_no_signals(self):
        """Test ticket with no risk signals."""
        ticket = Ticket(
            id="TEST-1",
            customer="Test",
            channel="email",
            last_message="Thank you for your help!",
            conversation_summary="Issue resolved satisfactorily",
            sla_hours_open=2
        )
        result = analyze_ticket(ticket)
        assert result.risk_label == RiskLabel.LOW
        assert result.reason == "No critical risk detected."
