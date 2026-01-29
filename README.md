# AI Support Intelligence

Backend API that analyzes customer support conversations to detect risk and prioritize actions.

## Features
- SLA risk detection
- Churn and escalation signals
- Actionable recommendations

## How it works
The system analyzes the latest customer message combined with a summarized conversation context to keep decisions fast and scalable.

## Setup

### Environment Variables
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## Run

### Local Development
```bash
uvicorn app.main:app --reload
```

### Docker
```bash
# Build and run with Docker
docker build -t ai-support-intelligence .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key ai-support-intelligence
```

### Docker Compose
```bash
# Start the service
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop the service
docker-compose down
```

The API will be available at `http://localhost:8000`
