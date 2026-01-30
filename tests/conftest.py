import pytest
from unittest.mock import MagicMock, patch
from app.models import Ticket, RiskLabel


@pytest.fixture
def sample_ticket_low_risk():
    """Low risk ticket fixture."""
    return Ticket(
        id="TICKET-001",
        customer="John Doe",
        channel="email",
        last_message="Can you help me with my account?",
        conversation_summary="Customer asked for account assistance.",
        sla_hours_open=2,
        language="en-US"
    )


@pytest.fixture
def sample_ticket_medium_risk():
    """Medium risk ticket fixture."""
    return Ticket(
        id="TICKET-002",
        customer="Jane Smith",
        channel="chat",
        last_message="I've been waiting for 24 hours with no response!",
        conversation_summary="Multiple follow-ups, issue not resolved.",
        sla_hours_open=48,
        language="en-US"
    )


@pytest.fixture
def sample_ticket_high_risk():
    """High risk ticket fixture with escalation intent."""
    return Ticket(
        id="TICKET-003",
        customer="Bob Johnson",
        channel="email",
        last_message="I'm contacting procon and my lawyer about this terrible service!",
        conversation_summary="Customer extremely frustrated, threatens legal action.",
        sla_hours_open=72,
        language="en-US"
    )


@pytest.fixture
def sample_ticket_churn():
    """Ticket with churn signals."""
    return Ticket(
        id="TICKET-004",
        customer="Alice Wilson",
        channel="email",
        last_message="I want to cancelar my subscription immediately.",
        conversation_summary="Multiple service complaints.",
        sla_hours_open=36,
        language="pt-BR"
    )


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client."""
    with patch('app.services.openai_client.client') as mock:
        mock.chat.completions.create = MagicMock()
        yield mock
