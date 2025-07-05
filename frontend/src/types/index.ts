export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatState {
  conversations: Conversation[];
  currentConversationId: string | null;
  isLoading: boolean;
  error: string | null;
}

export type Provider = 'ollama' | 'llamacpp';

export interface Model {
  name: string;
  provider: Provider;
  description?: string;
}

export interface ChatRequest {
  messages: Message[];
  stream?: boolean;
  model?: string;
  provider?: Provider;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponse {
  message: Message;
  conversation_id?: string;
}

export interface StreamChunk {
  content: string;
  done: boolean;
}