# Swift Neethi

A complete AI chat application with a React frontend and Python FastAPI backend, supporting local LLM providers like Ollama and llama.cpp.

![Swift Neethi Interface](https://img.shields.io/badge/Interface-ChatGPT--like-green)
![Backend](https://img.shields.io/badge/Backend-FastAPI-blue)
![Frontend](https://img.shields.io/badge/Frontend-React-blue)
![AI Providers](https://img.shields.io/badge/AI-Ollama%20%7C%20llama.cpp-orange)

## 🌟 Features

### Frontend (React TypeScript)
- 🎨 **ChatGPT-like Interface**: Beautiful dark theme with sidebar and chat area
- 💬 **Real-time Streaming**: Messages stream in real-time from AI
- 📱 **Responsive Design**: Works perfectly on desktop and mobile
- 💾 **Chat History**: Multiple conversations with automatic saving
- ⚡ **Fast & Lightweight**: Built with modern React and TypeScript

### Backend (Python FastAPI)
- 🤖 **Multi-Provider Support**: Seamlessly switch between Ollama and llama.cpp
- 🧠 **Agent Architecture**: Modular agents for chat, memory, and prompt management
- 📡 **Streaming API**: Real-time responses via Server-Sent Events
- 🎯 **System Prompts**: Dynamic prompt templates with variable substitution
- 🔒 **Rate Limiting**: Built-in protection and error handling
- 📊 **REST API**: Complete API with automatic documentation

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** 
- **Node.js 16+**
- **llama.cpp server** running at `http://127.0.0.1:1234` (or Ollama)

### Easy Setup (Recommended)
```bash
# Clone/navigate to the project directory
cd "Swift Neethi"

# Run the startup script (starts both backend and frontend)
./start.sh
```

This will:
- ✅ Check prerequisites
- 📦 Install all dependencies
- 🚀 Start backend at `http://localhost:8000`
- 🎨 Start frontend at `http://localhost:3000`
- 📚 Provide API docs at `http://localhost:8000/docs`

### Manual Setup

#### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python3 main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🏗️ Architecture

```
Swift Neethi/
├── 🖥️  frontend/          # React TypeScript UI
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── services/      # API integration
│   │   ├── types.ts       # TypeScript definitions
│   │   └── App.tsx        # Main application
├── 🔧 backend/            # Python FastAPI server
│   ├── app/
│   │   ├── agents/        # AI agent implementations
│   │   ├── providers/     # LLM provider interfaces
│   │   ├── routes/        # API endpoints
│   │   ├── models/        # Data models
│   │   └── middleware/    # Request processing
│   └── main.py           # FastAPI application
└── 📄 README.md          # This file
```

## 🔧 Configuration

### Backend Configuration (.env)
```bash
# Provider URLs
LLAMACPP_BASE_URL=http://127.0.0.1:1234
OLLAMA_BASE_URL=http://localhost:11434

# Default Models
LLAMACPP_DEFAULT_MODEL=qwen/qwen3-4b
OLLAMA_DEFAULT_MODEL=llama2

# Server Settings
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Agent Settings
MAX_CONTEXT_LENGTH=4096
DEFAULT_TEMPERATURE=0.7
```

### Frontend Configuration
The frontend automatically connects to the backend at `http://localhost:8000`. To change this, edit `frontend/src/services/api.ts`.

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send chat message |
| `/api/chat/stream` | POST | Stream chat response |
| `/api/models` | GET | List available models |
| `/api/models/providers` | GET | Check provider status |
| `/api/prompts` | GET/POST/PUT/DELETE | Manage system prompts |
| `/docs` | GET | Interactive API documentation |

## 🤖 Supported AI Providers

### llama.cpp
- ✅ **Chat Completions**: `/v1/chat/completions`
- ✅ **Streaming**: Real-time response streaming
- ✅ **Model List**: `/v1/models`
- ✅ **Multi-model**: Support for multiple loaded models

### Ollama
- ✅ **Chat API**: Native Ollama chat interface
- ✅ **Streaming**: Real-time response streaming
- ✅ **Model Management**: List and switch models
- ✅ **Auto-discovery**: Automatic model detection

## 🎯 Usage Examples

### Basic Chat
1. Open `http://localhost:3000`
2. Click "New Chat" to start
3. Type your message and press Enter
4. Watch the AI response stream in real-time

### System Prompts
Create custom AI personalities and contexts:
```json
{
  "name": "Code Helper",
  "content": "You are an expert programmer. Help with coding questions and provide clear examples.",
  "variables": ["language", "difficulty"]
}
```

### API Integration
```javascript
// Send a chat message
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Hello!' }],
    provider: 'llamacpp',
    model: 'qwen/qwen3-4b'
  })
});
```

## 🛠️ Development

### Testing the Backend
```bash
cd backend
python3 quick_test.py
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build

# Backend
cd backend
pip install gunicorn
gunicorn main:app
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🆘 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version: `python3 --version`
- Verify virtual environment: `source venv/bin/activate`
- Check port 8000 availability

**Frontend won't connect:**
- Ensure backend is running at `http://localhost:8000`
- Check browser console for CORS errors
- Verify API URL in `frontend/src/services/api.ts`

**llama.cpp not working:**
- Verify server is running at `http://127.0.0.1:1234`
- Test endpoints: `curl http://127.0.0.1:1234/v1/models`
- Check model is loaded properly

### Getting Help
- 📚 Check the API docs: `http://localhost:8000/docs`
- 🐛 Review browser console for errors
- 🔍 Check backend logs for detailed error messages

---

**Built with ❤️ for local AI development**