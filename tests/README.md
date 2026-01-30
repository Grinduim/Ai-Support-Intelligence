# Unit Tests Documentation

## Overview

Comprehensive unit test suite for the AI Support Intelligence API covering:
- Data model validation (Pydantic schemas)
- Heuristic risk analysis engine
- LLM-based analysis and reply generation
- API endpoints
- Integration workflows

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_models.py           # Data model validation tests
├── test_risk_analyzer.py    # Heuristic analysis tests
├── test_llm_engine.py       # LLM engine tests (mocked)
├── test_reply_suggester.py  # Reply generation tests (mocked)
└── test_endpoints.py        # API endpoint tests
```

## Running Tests

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_models.py
```

### Run Specific Test Class
```bash
pytest tests/test_models.py::TestTicketModel
```

### Run Specific Test Function
```bash
pytest tests/test_models.py::TestTicketModel::test_ticket_valid
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pytest --cov=app --cov-report=html
```

### Run Only Async Tests
```bash
pytest -m asyncio
```

### Run Excluding Async Tests
```bash
pytest -m "not asyncio"
```

## Test Coverage

### 1. **test_models.py** (40+ tests)
Tests data model validation using Pydantic:

#### Ticket Model
- ✅ Valid ticket creation
- ✅ `last_message` max length (255 chars)
- ✅ `conversation_summary` max length (255 chars)
- ✅ Language default value (en-US)
- ✅ Exactly 255 characters allowed
- ✅ Character limit enforcement

#### RiskLabel Enum
- ✅ Enum values (LOW, MEDIUM, HIGH)

#### TicketAnalyzeRequest
- ✅ Single ticket request
- ✅ Multiple tickets request

#### TicketResult
- ✅ Valid result creation
- ✅ Result structure validation

#### AIAnalysis
- ✅ Valid analysis creation
- ✅ Confidence bounds (0-100)
- ✅ Confidence at boundaries (0, 100)
- ✅ Out-of-bounds rejection

#### ReplySuggestionRequest
- ✅ Valid request creation
- ✅ Message length limits

#### ReplySuggestionResponse
- ✅ Valid response creation
- ✅ Confidence validation
- ✅ Default values

### 2. **test_risk_analyzer.py** (15+ tests)
Tests heuristic risk analysis engine:

- ✅ Low risk ticket detection
- ✅ High risk ticket detection (escalation)
- ✅ Medium risk ticket detection (SLA)
- ✅ Churn signal detection
- ✅ Risk breakdown structure
- ✅ Risk score bounds (0-100)
- ✅ SLA scoring (12h, 24h, 48h thresholds)
- ✅ Multiple keyword accumulation
- ✅ Language preservation
- ✅ Reason formatting
- ✅ No-risk scenario handling

### 3. **test_llm_engine.py** (12+ tests)
Tests LLM-based analysis (with mocked OpenAI API):

- ✅ Valid JSON response parsing
- ✅ High risk detection via LLM
- ✅ Confidence clamping (max 100)
- ✅ Confidence clamping (min 0)
- ✅ Risk score clamping
- ✅ Invalid risk label rejection
- ✅ Malformed JSON extraction
- ✅ Completely invalid JSON handling
- ✅ Language parameter passing
- ✅ Empty signals list handling

### 4. **test_reply_suggester.py** (10+ tests)
Tests LLM-based reply generation (with mocked OpenAI API):

- ✅ Valid reply suggestion
- ✅ High risk reply generation
- ✅ Language-specific replies (pt-BR, en-US)
- ✅ Confidence validation
- ✅ JSON parse error fallback
- ✅ Missing fields handling
- ✅ Default values
- ✅ Tone parameter passing (formal, friendly, technical)

### 5. **test_endpoints.py** (15+ tests)
Tests API endpoints:

#### Ticket Analysis Endpoint (`POST /tickets/analyze`)
- ✅ Single ticket analysis
- ✅ Multiple ticket analysis
- ✅ Invalid JSON rejection (422)
- ✅ Message length validation (422)
- ✅ Response structure validation

#### Reply Suggestion Endpoint (`POST /replies/suggest-reply`)
- ✅ Valid request handling
- ✅ Fallback on LLM error
- ✅ Message length validation
- ✅ Response structure validation

#### Health Check Endpoint (`GET /health`)
- ✅ Healthy status (OpenAI available)
- ✅ Degraded status (OpenAI unavailable)
- ✅ Response structure validation

#### Integration Tests
- ✅ Full ticket analysis workflow

## Test Fixtures

### In `conftest.py`:

#### `sample_ticket_low_risk`
Low risk ticket for testing.
```python
Ticket(
    id="TICKET-001",
    customer="John Doe",
    channel="email",
    last_message="Can you help me with my account?",
    conversation_summary="Customer asked for account assistance.",
    sla_hours_open=2,
    language="en-US"
)
```

#### `sample_ticket_medium_risk`
Medium risk ticket (SLA aging).
```python
Ticket(
    id="TICKET-002",
    customer="Jane Smith",
    channel="chat",
    last_message="I've been waiting for 24 hours with no response!",
    conversation_summary="Multiple follow-ups, issue not resolved.",
    sla_hours_open=24,
    language="en-US"
)
```

#### `sample_ticket_high_risk`
High risk ticket (escalation threat).
```python
Ticket(
    id="TICKET-003",
    customer="Bob Johnson",
    channel="email",
    last_message="I'm contacting procon and my lawyer about this terrible service!",
    conversation_summary="Customer extremely frustrated, threatens legal action.",
    sla_hours_open=72,
    language="en-US"
)
```

#### `sample_ticket_churn`
Ticket with churn signals.
```python
Ticket(
    id="TICKET-004",
    customer="Alice Wilson",
    channel="email",
    last_message="I want to cancelar my subscription immediately.",
    conversation_summary="Multiple service complaints.",
    sla_hours_open=36,
    language="pt-BR"
)
```

#### `mock_openai_client`
Mocked OpenAI client for isolation testing.

## Mocking Strategy

### OpenAI API Mocks
All tests that require LLM calls use `@patch` decorator to mock `openai_chat`:

```python
@pytest.mark.asyncio
async def test_analyze_with_llm_valid_response(self, sample_ticket_low_risk):
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
        assert result.confidence == 85
```

### Benefits
- ✅ Tests run without OpenAI API calls
- ✅ Reproducible results (no API variability)
- ✅ Faster test execution
- ✅ No API costs
- ✅ Easy error scenario simulation

## Key Test Patterns

### 1. Validation Testing
```python
def test_ticket_last_message_max_length(self):
    with pytest.raises(ValidationError) as exc_info:
        Ticket(last_message="x" * 256)
    assert "max_length" in str(exc_info.value).lower()
```

### 2. Boundary Testing
```python
def test_confidence_at_boundaries(self):
    analysis_0 = AIAnalysis(..., confidence=0)
    assert analysis_0.confidence == 0
    
    analysis_100 = AIAnalysis(..., confidence=100)
    assert analysis_100.confidence == 100
```

### 3. Async Testing
```python
@pytest.mark.asyncio
async def test_analyze_with_llm_valid_response(self):
    with patch('app.services.llm_engine.openai_chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = json.dumps(mock_response)
        result = await analyze_with_llm(ticket)
```

### 4. Error Handling Testing
```python
def test_json_parse_error_fallback(self):
    with patch('app.services.reply_suggester.openai_chat', new_callable=AsyncMock) as mock_chat:
        mock_chat.return_value = "Invalid JSON"
        with pytest.raises(Exception):
            await suggest_reply_with_llm(request)
```

### 5. Integration Testing
```python
def test_full_workflow(self):
    response = client.post("/tickets/analyze", json=payload)
    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
```

## Test Metrics

| Metric | Value |
|--------|-------|
| **Total Tests** | ~90+ |
| **Test Files** | 5 |
| **Fixtures** | 5 |
| **Coverage Target** | >80% |
| **Execution Time** | <10 seconds (mocked) |

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Debugging Tests

### Run Single Test with Debug Output
```bash
pytest tests/test_models.py::TestTicketModel::test_ticket_valid -vv --tb=long
```

### Run with Print Statements
```bash
pytest -s tests/test_models.py
```

### Run and Stop on First Failure
```bash
pytest -x tests/
```

### Run Last Failed Tests
```bash
pytest --lf tests/
```

### Run Tests in Parallel (optional with pytest-xdist)
```bash
pip install pytest-xdist
pytest -n auto tests/
```

## Best Practices

1. ✅ **Isolation**: Each test is independent; fixtures reset state
2. ✅ **Clarity**: Test names clearly describe what's being tested
3. ✅ **Mocking**: External APIs (OpenAI) are mocked to avoid dependencies
4. ✅ **Coverage**: Both happy paths and error cases tested
5. ✅ **Speed**: Tests run in <10 seconds (important for CI/CD)
6. ✅ **Assertions**: Clear, specific assertions with good error messages
7. ✅ **Documentation**: Each test class has a docstring explaining purpose

## Future Enhancements

- [ ] Add performance benchmarking tests
- [ ] Add database persistence tests (when DB is added)
- [ ] Add authentication/authorization tests (when added)
- [ ] Add rate limiting tests (when implemented)
- [ ] Add E2E tests with real OpenAI API (smoke tests)
- [ ] Add property-based testing with Hypothesis
- [ ] Add mutation testing for test quality
