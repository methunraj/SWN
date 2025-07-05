import axios from 'axios';
import { Message, Conversation, Provider, Model, ChatRequest, ChatResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatAPI = {
  sendMessage: async (messages: Message[], options?: Partial<ChatRequest>): Promise<ChatResponse> => {
    const response = await api.post('/api/chat', {
      messages,
      ...options,
    });
    return response.data;
  },

  streamMessage: async (
    messages: Message[], 
    options: Partial<ChatRequest> = {}, 
    onChunk: (chunk: string) => void,
    onError?: (error: Error) => void
  ) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          messages, 
          stream: true, 
          ...options 
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.content) {
                onChunk(parsed.content);
              }
            } catch (e) {
              console.error('Error parsing chunk:', e);
            }
          }
        }
      }
    } catch (error) {
      if (onError) {
        onError(error as Error);
      } else {
        throw error;
      }
    }
  },

  getConversations: async (): Promise<Conversation[]> => {
    const response = await api.get('/api/chat/conversations');
    return response.data;
  },

  getConversation: async (id: string): Promise<Conversation> => {
    const response = await api.get(`/api/chat/conversations/${id}`);
    return response.data;
  },

  deleteConversation: async (id: string): Promise<void> => {
    await api.delete(`/api/chat/conversations/${id}`);
  },

  getModels: async (): Promise<Model[]> => {
    const response = await api.get('/api/models');
    return response.data;
  },

  getPrompts: async () => {
    const response = await api.get('/api/prompts');
    return response.data;
  },

  createPrompt: async (data: any) => {
    const response = await api.post('/api/prompts', data);
    return response.data;
  },

  updatePrompt: async (id: string, data: any) => {
    const response = await api.put(`/api/prompts/${id}`, data);
    return response.data;
  },

  deletePrompt: async (id: string) => {
    await api.delete(`/api/prompts/${id}`);
  },
};