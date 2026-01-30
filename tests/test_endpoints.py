import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.models import RiskLabel
import json


client = TestClient(app)


class TestTicketsEndpoint:
    """Test ticket analysis endpoint."""
    
    def test_analyze_ticket_endpoint_single(self):
        """Test POST /tickets/analyze with single ticket."""
        payload = {
            "tickets": [
                {
                    "id": "TICKET-001",
                    "customer": "John Doe",
                    "channel": "email",
                    "last_message": "Can you help me?",
                    "conversation_summary": "Customer needs help",
                    "sla_hours_open": 5,
                    "language": "en-US"
                }
            ]
        }
        
        response = client.post("/tickets/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == "TICKET-001"
        assert "risk_score" in data["results"][0]
        assert "risk_label" in data["results"][0]
    
    def test_analyze_ticket_endpoint_multiple(self):
        """Test POST /tickets/analyze with multiple tickets."""
        payload = {
            "tickets": [
                {
                    "id": f"TICKET-{i:03d}",
                    "customer": f"Customer {i}",
                    "channel": "email",
                    "last_message": "Help",
                    "conversation_summary": "Summary",
                    "sla_hours_open": i * 10,
                    "language": "en-US"
                }
                for i in range(1, 4)
            ]
        }
        
        response = client.post("/tickets/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 3
    
    def test_analyze_ticket_invalid_json(self):
        """Test invalid JSON structure."""
        payload = {
            "tickets": [
                {
                    # Missing required fields
                    "id": "TICKET-001"
                }
            ]
        }
        
        response = client.post("/tickets/analyze", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_ticket_message_too_long(self):
        """Test message exceeding 255 character limit."""
        payload = {
            "tickets": [
                {
                    "id": "TICKET-001",
                    "customer": "John Doe",
                    "channel": "email",
                    "last_message": "x" * 256,  # Exceeds 255
                    "conversation_summary": "Valid",
                    "sla_hours_open": 5
                }
            ]
        }
        
        response = client.post("/tickets/analyze", json=payload)
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_ticket_response_structure(self):
        """Test response has correct structure."""
        payload = {
            "tickets": [
                {
                    "id": "TICKET-001",
                    "customer": "John Doe",
                    "channel": "email",
                    "last_message": "Help!",
                    "conversation_summary": "Summary",
                    "sla_hours_open": 10
                }
            ]
        }
        
        response = client.post("/tickets/analyze", json=payload)
        
        assert response.status_code == 200
        result = response.json()["results"][0]
        
        # Verify all required fields
        assert result["id"] == "TICKET-001"
        assert isinstance(result["risk_score"], int)
        assert 0 <= result["risk_score"] <= 100
        assert result["risk_label"] in ["LOW", "MEDIUM", "HIGH"]
        assert isinstance(result["reason"], str)
        assert isinstance(result["suggested_action"], str)
        assert isinstance(result["debug_signals"], list)
        assert isinstance(result["risk_breakdown"], dict)


class TestRepliesEndpoint:
    """Test reply suggestion endpoint."""
    
    @patch('app.services.reply_suggester.openai_chat')
    def test_suggest_reply_endpoint(self, mock_chat):
        """Test POST /replies/suggest-reply endpoint."""
        mock_chat.return_value = json.dumps({
            "reply_text": "Thank you for contacting us.",
            "confidence": 85,
            "subject": "We're here to help",
            "next_steps": ["Follow up"],
            "do_not_say": ["No"]
        })
        
        payload = {
            "ticket_id": "TICKET-001",
            "customer": "John Doe",
            "channel": "email",
            "last_message": "Help!",
            "conversation_summary": "Summary",
            "risk_label": "LOW",
            "company_tone": "friendly",
            "language": "en-US"
        }
        
        response = client.post("/replies/suggest-reply", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["ticket_id"] == "TICKET-001"
        assert data["confidence"] == 85
        assert "suggested_reply" in data
    
    @patch('app.services.reply_suggester.openai_chat')
    def test_suggest_reply_fallback_on_error(self, mock_chat):
        """Test fallback reply when LLM fails."""
        mock_chat.side_effect = Exception("LLM Error")
        
        payload = {
            "ticket_id": "TICKET-001",
            "customer": "John Doe",
            "channel": "email",
            "last_message": "Help!",
            "conversation_summary": "Summary",
            "risk_label": "HIGH",
            "company_tone": "formal",
            "language": "en-US"
        }
        
        response = client.post("/replies/suggest-reply", json=payload)
        
        # Should return fallback with confidence=0
        assert response.status_code == 200
        data = response.json()
        assert data["confidence"] == 0
        assert "shortly" in data["suggested_reply"].lower()
    
    def test_suggest_reply_invalid_language(self):
        """Test message exceeding length limit."""
        payload = {
            "ticket_id": "TICKET-001",
            "customer": "John Doe",
            "channel": "email",
            "last_message": "x" * 256,  # Exceeds 255
            "conversation_summary": "Summary",
            "risk_label": "LOW",
            "company_tone": "friendly",
            "language": "en-US"
        }
        
        response = client.post("/replies/suggest-reply", json=payload)
        
        assert response.status_code == 422
    
    @patch('app.services.reply_suggester.openai_chat')
    def test_suggest_reply_response_structure(self, mock_chat):
        """Test response structure."""
        mock_chat.return_value = json.dumps({
            "reply_text": "Response",
            "confidence": 75,
            "subject": "Subject",
            "next_steps": ["Step1", "Step2"],
            "do_not_say": ["Word1"]
        })
        
        payload = {
            "ticket_id": "TICKET-001",
            "customer": "John Doe",
            "channel": "email",
            "last_message": "Help",
            "conversation_summary": "Summary",
            "risk_label": "MEDIUM",
            "company_tone": "friendly",
            "language": "en-US"
        }
        
        response = client.post("/replies/suggest-reply", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["ticket_id"] == "TICKET-001"
        assert isinstance(data["suggested_reply"], str)
        assert 0 <= data["confidence"] <= 100
        assert data["language"] == "en-US"
        assert isinstance(data["subject"], str)
        assert isinstance(data["next_steps"], list)
        assert isinstance(data["do_not_say"], list)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    @patch('app.routes.health.client.models.list')
    def test_health_check_healthy(self, mock_models):
        """Test health endpoint when OpenAI is available."""
        mock_models.return_value = MagicMock()
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "AI Support Intelligence"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert isinstance(data["openai_available"], bool)
    
    @patch('app.routes.health.client.models.list')
    def test_health_check_degraded(self, mock_models):
        """Test health endpoint when OpenAI is unavailable."""
        mock_models.side_effect = Exception("OpenAI Error")
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["openai_available"] is False
    
    def test_health_check_response_structure(self):
        """Test health response structure."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "service" in data
        assert "version" in data
        assert "openai_available" in data
        
        # Verify timestamp format (ISO format)
        assert "T" in data["timestamp"]
        assert "Z" in data["timestamp"]


class TestEndpointIntegration:
    """Integration tests for endpoint workflows."""
    
    @patch('app.services.risk_analyzer.analyze_ticket')
    def test_full_ticket_analysis_workflow(self, mock_analyzer):
        """Test complete ticket analysis workflow."""
        from app.models import TicketResult, RiskLabel
        
        mock_result = TicketResult(
            id="TICKET-001",
            risk_score=75,
            risk_label=RiskLabel.HIGH,
            reason="Test",
            suggested_action="Test",
            debug_signals=["test"],
            risk_breakdown={"escalation": 40, "churn": 0, "sla": 35, "sentiment": 0}
        )
        mock_analyzer.return_value = mock_result
        
        payload = {
            "tickets": [
                {
                    "id": "TICKET-001",
                    "customer": "John Doe",
                    "channel": "email",
                    "last_message": "Help!",
                    "conversation_summary": "Summary",
                    "sla_hours_open": 50
                }
            ]
        }
        
        response = client.post("/tickets/analyze", json=payload)
        
        assert response.status_code == 200
        assert response.json()["results"][0]["risk_label"] == "HIGH"
