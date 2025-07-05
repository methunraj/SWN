export const DEFAULT_SYSTEM_PROMPT = `You are a helpful AI assistant. Provide clear, accurate, and helpful responses to user queries.`;

export const WELCOME_MESSAGES = [
  "Hello! How can I assist you today?",
  "Welcome! What would you like to know?",
  "Hi there! I'm here to help. What's on your mind?",
];

export const EXAMPLE_PROMPTS = [
  {
    title: "Explain a concept",
    prompt: "Explain quantum computing in simple terms",
    icon: "academic-cap",
  },
  {
    title: "Write code",
    prompt: "Write a Python function to calculate fibonacci numbers",
    icon: "code-bracket",
  },
  {
    title: "Creative writing",
    prompt: "Write a short story about a time traveler",
    icon: "pencil",
  },
  {
    title: "Analyze data",
    prompt: "What are the key trends in renewable energy adoption?",
    icon: "chart-bar",
  },
];

export const KEYBOARD_SHORTCUTS = {
  NEW_CHAT: { key: 'n', ctrlKey: true },
  SEARCH: { key: '/', ctrlKey: true },
  TOGGLE_SIDEBAR: { key: 'b', ctrlKey: true },
  SETTINGS: { key: ',', ctrlKey: true },
  SEND_MESSAGE: { key: 'Enter', ctrlKey: false },
  NEW_LINE: { key: 'Enter', shiftKey: true },
};