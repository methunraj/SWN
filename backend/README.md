# Swift Neethi Backend

A Python FastAPI backend that supports both Ollama and llama.cpp for local LLM inference with an agent-based architecture.

## Features

- **Multi-Provider Support**: Seamlessly switch between Ollama and llama.cpp
- **Agent System**: Modular agent architecture with:
  - **ChatAgent**: Orchestrates conversation flow
  - **MemoryAgent**: Manages conversation history and context
  - **SystemPromptAgent**: Handles system prompts and templates
- **Streaming Support**: Real-time responses via Server-Sent Events
- **System Prompt Management**: Create, update, and manage system prompts
- **Conversation Memory**: Automatic context management and conversation history
- **Rate Limiting**: Built-in rate limiting for API protection
- **CORS Support**: Configurable CORS for frontend integration

## Installation

1. Clone the repository and navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file:
```bash
cp .env.example .env
```

5. Configure your `.env` file with appropriate settings.

## Configuration

Edit the `.env` file to configure:

- **Server Settings**: Host, port, debug mode
- **Provider URLs**: Ollama and llama.cpp endpoints
- **Default Models**: Default models for each provider
- **Agent Settings**: Context length, temperature, etc.
- **Security**: Secret keys and tokens
- **Rate Limiting**: Requests per minute

## Running the Server

### Development Mode
```bash
python main.py
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Chat
- `POST /api/chat` - Send a chat message
- `POST /api/chat/stream` - Stream chat responses
- `GET /api/chat/conversations/{id}` - Get conversation history
- `DELETE /api/chat/conversations/{id}` - Delete conversation

### Models
- `GET /api/models` - List available models
- `GET /api/models/providers` - Check provider status
- `POST /api/models/test/{provider}` - Test provider connectivity

### System Prompts
- `GET /api/prompts` - List all prompts
- `GET /api/prompts/{id}` - Get specific prompt
- `POST /api/prompts` - Create new prompt
- `PUT /api/prompts/{id}` - Update prompt
- `DELETE /api/prompts/{id}` - Delete prompt
- `POST /api/prompts/validate` - Validate prompt template

### Health & Info
- `GET /` - API info
- `GET /health` - Health check

## Usage Examples

### Basic Chat Request
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/chat",
        json={
            "messages": [
                {"role": "user", "content": "Hello!"}
            ],
            "provider": "ollama",
            "model": "llama2"
        }
    )
    print(response.json())
```

### Streaming Chat
```python
import httpx

async with httpx.AsyncClient() as client:
    async with client.stream(
        "POST",
        "http://localhost:8000/api/chat/stream",
        json={
            "messages": [
                {"role": "user", "content": "Tell me a story"}
            ],
            "stream": True
        }
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                print(line[6:])
```

### Using System Prompts
```python
# Create a custom prompt
response = await client.post(
    "http://localhost:8000/api/prompts",
    json={
        "name": "Python Expert",
        "content": "You are a Python expert. Current time: {datetime}",
        "description": "Expert Python programming assistant"
    }
)

# Use the prompt in chat
response = await client.post(
    "http://localhost:8000/api/chat",
    json={
        "messages": [{"role": "user", "content": "How do I use async/await?"}],
        "system_prompt_id": "python_expert"
    }
)
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/
flake8 app/
mypy app/
```

## Architecture

The backend uses a modular agent-based architecture:

1. **Providers**: Abstract interface for LLM providers (Ollama, llama.cpp)
2. **Agents**: Specialized agents for different tasks
3. **Routes**: FastAPI routes for API endpoints
4. **Models**: Pydantic models for request/response validation
5. **Middleware**: CORS, rate limiting, error handling

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

MIT License