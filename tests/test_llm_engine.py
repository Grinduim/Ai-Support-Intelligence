import pytest
import json
from unittest.mock import AsyncMock, patch
from app.services.llm_engine import analyze_with_llm
from app.models import Ticket, RiskLabel, AIAnalysis


class TestLLMEngine:
    """Test LLM-based risk analysis."""
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_valid_response(self, sample_ticket_low_risk):
        """Test successful LLM analysis with valid JSON response."""
        mock_response = {
            "risk_score": 30,
            "risk_label": "LOW",
            "reason": "Low risk ticket",
            "suggested_action": "Standard response",
            "confidence": 85,
            "signals": ["no_escalation"]
        }
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await analyze_with_llm(sample_ticket_low_risk)
            
            assert isinstance(result, AIAnalysis)
            assert result.risk_score == 30
            assert result.risk_label == RiskLabel.LOW
            assert result.confidence == 85
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_high_risk(self, sample_ticket_high_risk):
        """Test LLM analysis identifies high risk."""
        mock_response = {
            "risk_score": 95,
            "risk_label": "HIGH",
            "reason": "Customer threatening legal action",
            "suggested_action": "Escalate immediately to senior management",
            "confidence": 98,
            "signals": ["escalation_threat", "legal_mention"]
        }
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await analyze_with_llm(sample_ticket_high_risk)
            
            assert result.risk_label == RiskLabel.HIGH
            assert result.confidence == 98
            assert len(result.signals) == 2
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_confidence_clamped_high(self, sample_ticket_low_risk):
        """Test confidence is clamped to max 100."""
        mock_response = {
            "risk_score": 30,
            "risk_label": "LOW",
            "reason": "Test",
            "suggested_action": "Test",
            "confidence": 150  # Invalid: > 100
        }
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await analyze_with_llm(sample_ticket_low_risk)
            
            assert result.confidence == 100  # Clamped
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_confidence_clamped_low(self, sample_ticket_low_risk):
        """Test confidence is clamped to min 0."""
        mock_response = {
            "risk_score": 30,
            "risk_label": "LOW",
            "reason": "Test",
            "suggested_action": "Test",
            "confidence": -50  # Invalid: < 0
        }
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await analyze_with_llm(sample_ticket_low_risk)
            
            assert result.confidence == 0  # Clamped
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_risk_score_clamped(self, sample_ticket_low_risk):
        """Test risk_score is clamped to 0-100."""
        mock_response = {
            "risk_score": 250,  # Invalid: > 100
            "risk_label": "HIGH",
            "reason": "Test",
            "suggested_action": "Test",
            "confidence": 50
        }
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await analyze_with_llm(sample_ticket_low_risk)
            
            assert result.risk_score == 100  # Clamped
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_invalid_risk_label(self, sample_ticket_low_risk):
        """Test invalid risk_label raises error."""
        mock_response = {
            "risk_score": 50,
            "risk_label": "CRITICAL",  # Invalid: not in enum
            "reason": "Test",
            "suggested_action": "Test",
            "confidence": 50
        }
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            with pytest.raises(ValueError) as exc_info:
                await analyze_with_llm(sample_ticket_low_risk)
            
            assert "input should be 'low', 'medium' or 'high'" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_malformed_json(self, sample_ticket_low_risk):
        """Test handling of malformed JSON with extraction."""
        malformed_response = """
        Some text before JSON
        {
            "risk_score": 60,
            "risk_label": "MEDIUM",
            "reason": "Test",
            "suggested_action": "Test",
            "confidence": 75
        }
        Some text after JSON
        """
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = malformed_response
            
            result = await analyze_with_llm(sample_ticket_low_risk)
            
            assert result.risk_label == RiskLabel.MEDIUM
            assert result.confidence == 75
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_completely_invalid_json(self, sample_ticket_low_risk):
        """Test handling of completely invalid JSON."""
        invalid_response = "This is not JSON at all"
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = invalid_response
            
            with pytest.raises(ValueError) as exc_info:
                await analyze_with_llm(sample_ticket_low_risk)
            
            assert "invalid json" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_language_respected(self):
        """Test that language is passed correctly to LLM."""
        ticket_pt = Ticket(
            id="TEST-PT",
            customer="João",
            channel="email",
            last_message="Cancelar",
            conversation_summary="Reclamação",
            sla_hours_open=24,
            language="pt-BR"
        )
        
        mock_response = {
            "risk_score": 80,
            "risk_label": "HIGH",
            "reason": "Cliente quer cancelar",
            "suggested_action": "Escalação urgente",
            "confidence": 90
        }
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await analyze_with_llm(ticket_pt)
            
            # Verify language was passed in the prompt
            call_args = mock_chat.call_args
            user_prompt = call_args.kwargs['user'] if 'user' in call_args.kwargs else call_args[0][1]
            assert "pt-BR" in user_prompt
    
    @pytest.mark.asyncio
    async def test_analyze_with_llm_empty_signals_list(self, sample_ticket_low_risk):
        """Test handling of missing signals field."""
        mock_response = {
            "risk_score": 30,
            "risk_label": "LOW",
            "reason": "Test",
            "suggested_action": "Test",
            "confidence": 75
            # No signals field
        }
        
        with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await analyze_with_llm(sample_ticket_low_risk)
            
            assert result.signals == []
