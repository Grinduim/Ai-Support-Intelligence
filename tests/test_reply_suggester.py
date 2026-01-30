import pytest
import json
from unittest.mock import AsyncMock, patch
from app.services.reply_suggester import suggest_reply_with_llm
from app.models import ReplySuggestionRequest, ReplySuggestionResponse, RiskLabel


class TestReplySuggester:
    """Test LLM-based reply suggestion."""
    
    @pytest.mark.asyncio
    async def test_suggest_reply_valid_response(self):
        """Test successful reply suggestion."""
        request = ReplySuggestionRequest(
            ticket_id="TICKET-001",
            customer="John Doe",
            channel="email",
            last_message="Help please!",
            conversation_summary="Customer needs assistance",
            risk_label=RiskLabel.MEDIUM,
            company_tone="friendly",
            language="en-US"
        )
        
        mock_response = {
            "reply_text": "Thank you for reaching out. We're here to help and will get back to you shortly.",
            "subject": "We're here to assist",
            "next_steps": ["Investigate issue", "Contact customer within 2 hours"],
            "do_not_say": ["We can't help you"],
            "confidence": 88
        }
        
        with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await suggest_reply_with_llm(request)
            
            assert isinstance(result, ReplySuggestionResponse)
            assert result.ticket_id == "TICKET-001"
            assert result.confidence == 88
            assert "help" in result.suggested_reply.lower()
    
    @pytest.mark.asyncio
    async def test_suggest_reply_high_risk(self):
        """Test reply suggestion for high risk ticket."""
        request = ReplySuggestionRequest(
            ticket_id="TICKET-002",
            customer="Jane Smith",
            channel="chat",
            last_message="I'm canceling immediately!",
            conversation_summary="Very upset customer",
            risk_label=RiskLabel.HIGH,
            company_tone="formal",
            language="en-US"
        )
        
        mock_response = {
            "reply_text": "Dear Jane, We deeply apologize for the inconvenience. A senior manager will contact you within 30 minutes with a resolution plan.",
            "subject": "Urgent: Your concern is our priority",
            "next_steps": ["Assign to senior manager", "Prepare retention offer"],
            "do_not_say": ["That's our policy"],
            "confidence": 95
        }
        
        with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await suggest_reply_with_llm(request)
            
            assert result.confidence == 95
            assert "apologize" in result.suggested_reply.lower()
            assert "manager" in result.suggested_reply.lower()
    
    @pytest.mark.asyncio
    async def test_suggest_reply_language_respect(self):
        """Test reply is generated in requested language."""
        request = ReplySuggestionRequest(
            ticket_id="TICKET-003",
            customer="Maria",
            channel="email",
            last_message="Quero cancelar",
            conversation_summary="Cliente insatisfeito",
            risk_label=RiskLabel.HIGH,
            company_tone="friendly",
            language="pt-BR"
        )
        
        mock_response = {
            "reply_text": "Olá Maria, lamentamos muito sua insatisfação. Um gerente sênior entrará em contato em 30 minutos.",
            "subject": "Sua situação é nossa prioridade",
            "next_steps": ["Contatar gerente", "Oferecer solução"],
            "do_not_say": ["Esse é nosso processo"],
            "confidence": 92
        }
        
        with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            result = await suggest_reply_with_llm(request)
            
            assert result.language == "pt-BR"
            assert "gerente" in result.suggested_reply.lower()
    
    @pytest.mark.asyncio
    async def test_suggest_reply_confidence_validation(self):
        """Test confidence is validated within 0-100."""
        request = ReplySuggestionRequest(
            ticket_id="TICKET-004",
            customer="Test",
            channel="email",
            last_message="Help",
            conversation_summary="Summary",
            risk_label=RiskLabel.LOW,
            company_tone="formal",
            language="en-US"
        )
        
        # Test invalid confidence (>100)
        mock_response = {
            "reply_text": "Help text",
            "confidence": 150  # Invalid
        }
        
        with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(mock_response)
            
            # The service should catch and return fallback on validation error
            result = await suggest_reply_with_llm(request)
            
            # Fallback response should have confidence=0
            assert result.confidence <= 100
    
    @pytest.mark.asyncio
    async def test_suggest_reply_json_parse_error_fallback(self):
        """Test fallback on JSON parse error."""
        request = ReplySuggestionRequest(
            ticket_id="TICKET-005",
            customer="Test",
            channel="email",
            last_message="Help",
            conversation_summary="Summary",
            risk_label=RiskLabel.LOW,
            company_tone="formal",
            language="en-US"
        )
        
        # Invalid JSON response
        invalid_response = "This is not JSON"
        
        with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = invalid_response
            
            with pytest.raises(Exception) as exc_info:
                await suggest_reply_with_llm(request)
            
            assert "parse" in str(exc_info.value).lower() or "json" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_suggest_reply_missing_fields_fallback(self):
        """Test handling of missing required fields in LLM response."""
        request = ReplySuggestionRequest(
            ticket_id="TICKET-006",
            customer="Test",
            channel="email",
            last_message="Help",
            conversation_summary="Summary",
            risk_label=RiskLabel.LOW,
            company_tone="formal",
            language="en-US"
        )
        
        # Missing reply_text field
        incomplete_response = {
            "confidence": 50
            # Missing reply_text
        }
        
        with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(incomplete_response)
            
            result = await suggest_reply_with_llm(request)
            
            # Should use fallback reply text
            assert result.suggested_reply == "Thank you for reaching out. We will get back to you shortly."
            assert result.confidence == 50
            assert result.ticket_id == "TICKET-006"
    
    @pytest.mark.asyncio
    async def test_suggest_reply_default_values(self):
        """Test default values in response."""
        request = ReplySuggestionRequest(
            ticket_id="TICKET-007",
            customer="Test",
            channel="email",
            last_message="Help",
            conversation_summary="Summary",
            risk_label=RiskLabel.LOW,
            company_tone="formal",
            language="en-US"
        )
        
        minimal_response = {
            "reply_text": "Thank you for contacting us.",
            "confidence": 70
        }
        
        with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = json.dumps(minimal_response)
            
            result = await suggest_reply_with_llm(request)
            
            assert result.suggested_reply == "Thank you for contacting us."
            assert result.confidence == 70
            assert result.subject == ""
            assert result.next_steps == []
            assert result.do_not_say == []
    
    @pytest.mark.asyncio
    async def test_suggest_reply_tone_respected(self):
        """Test that company tone is passed to LLM."""
        tones = ["formal", "friendly", "technical"]
        
        for tone in tones:
            request = ReplySuggestionRequest(
                ticket_id="TICKET-008",
                customer="Test",
                channel="email",
                last_message="Help",
                conversation_summary="Summary",
                risk_label=RiskLabel.LOW,
                company_tone=tone,
                language="en-US"
            )
            
            mock_response = {
                "reply_text": f"Response in {tone} tone",
                "confidence": 80
            }
            
            with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
                mock_chat.return_value = json.dumps(mock_response)
                
                result = await suggest_reply_with_llm(request)
                
                # Verify tone was passed in the prompt
                call_args = mock_chat.call_args
                user_prompt = call_args.kwargs['user'] if 'user' in call_args.kwargs else call_args[0][1]
                assert tone in user_prompt
