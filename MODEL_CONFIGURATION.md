# Swift Neethi Model Configuration Guide

## 🎯 Setting Default Model

Swift Neethi allows you to configure which AI model to use by default through environment variables.

### Backend Configuration (.env)

Edit `/backend/.env` to set your default model:

```env
# Default Model Settings
DEFAULT_PROVIDER=llamacpp              # Options: ollama, llamacpp
DEFAULT_MODEL=qwen/qwen3-4b           # Model name
DEFAULT_TEMPERATURE=0.7               # 0.0-2.0 (creativity level)
DEFAULT_MAX_TOKENS=2048               # Maximum response length
DEFAULT_TOP_P=0.9                     # Nucleus sampling parameter
```

### Frontend Configuration (.env)

Edit `/frontend/.env` to match backend settings:

```env
# Default Model Settings
REACT_APP_DEFAULT_PROVIDER=llamacpp
REACT_APP_DEFAULT_MODEL=qwen/qwen3-4b
REACT_APP_DEFAULT_TEMPERATURE=0.7
REACT_APP_DEFAULT_MAX_TOKENS=2048
```

## 📊 Available Models

### For Ollama (http://localhost:11434)
- `llama2` - Meta's Llama 2 model
- `mistral` - Mistral 7B
- `codellama` - Code-optimized Llama
- `mixtral` - Mixtral 8x7B
- `neural-chat` - Intel's Neural Chat
- `phi` - Microsoft's Phi-2
- `vicuna` - Vicuna model

### For llama.cpp (http://127.0.0.1:1234)
- Use the model name as configured in your llama.cpp server
- Common format: `modelname/version` (e.g., `qwen/qwen3-4b`)

## 🔄 Switching Models

To switch models:

1. Stop the servers (Ctrl+C)
2. Update both `.env` files with new model settings
3. Restart using `./start.sh`

## 🧪 Testing Different Models

You can test different models without changing defaults by passing them in the API request:

```javascript
// In frontend code
await chatAPI.streamMessage(messages, {
  model: "mistral",
  provider: "ollama",
  temperature: 0.8
});
```

## ⚡ Performance Tips

- **Fast responses**: Use smaller models (7B parameters or less)
- **Better quality**: Use larger models (13B+ parameters)
- **Code tasks**: Use specialized models like `codellama`
- **General chat**: Use models like `llama2` or `mistral`

## 🚨 Troubleshooting

If you get model-related errors:

1. **Check provider is running**:
   - Ollama: `curl http://localhost:11434/api/tags`
   - llama.cpp: `curl http://127.0.0.1:1234/v1/models`

2. **Verify model is available**:
   - For Ollama: `ollama list`
   - For llama.cpp: Check your server configuration

3. **Match model names exactly**:
   - Model names are case-sensitive
   - Include version tags if required (e.g., `:latest`)

4. **Check logs**:
   - Backend: `tail -f backend/backend.log`
   - Frontend: Browser console (F12)