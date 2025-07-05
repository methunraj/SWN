import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { Message, Conversation, ChatState } from '../types';
import { chatAPI } from '../services/api';
import { storage } from '../services/storage';
import { createMessage, createConversation, generateConversationTitle } from '../utils/helpers';
import toast from 'react-hot-toast';

interface ChatContextType extends ChatState {
  sendMessage: (content: string) => Promise<void>;
  regenerateLastMessage: () => Promise<void>;
  createNewConversation: () => void;
  switchConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, title: string) => void;
  clearConversations: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};

interface ChatProviderProps {
  children: React.ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [state, setState] = useState<ChatState>({
    conversations: [],
    currentConversationId: null,
    isLoading: false,
    error: null,
  });

  // Load data from localStorage on mount
  useEffect(() => {
    const conversations = storage.getConversations();
    const currentId = storage.getCurrentConversationId();
    
    setState(prev => ({
      ...prev,
      conversations,
      currentConversationId: currentId,
    }));
  }, []);

  // Save to localStorage whenever conversations change
  useEffect(() => {
    storage.saveConversations(state.conversations);
  }, [state.conversations]);

  // Save current conversation ID
  useEffect(() => {
    storage.setCurrentConversationId(state.currentConversationId);
  }, [state.currentConversationId]);

  const getCurrentConversation = useCallback((): Conversation | null => {
    if (!state.currentConversationId) return null;
    return state.conversations.find(c => c.id === state.currentConversationId) || null;
  }, [state.conversations, state.currentConversationId]);

  const updateConversation = useCallback((id: string, updates: Partial<Conversation>) => {
    setState(prev => ({
      ...prev,
      conversations: prev.conversations.map(c =>
        c.id === id ? { ...c, ...updates, updatedAt: new Date() } : c
      ),
    }));
  }, []);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return;

    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      let conversation = getCurrentConversation();
      
      // Create new conversation if none exists
      if (!conversation) {
        conversation = createConversation();
        setState(prev => ({
          ...prev,
          conversations: [...prev.conversations, conversation!],
          currentConversationId: conversation!.id,
        }));
      }

      // Add user message
      const userMessage = createMessage(content, 'user');
      updateConversation(conversation.id, {
        messages: [...conversation.messages, userMessage],
      });

      // Generate title from first message
      if (conversation.messages.length === 0) {
        const title = generateConversationTitle(content);
        updateConversation(conversation.id, { title });
      }

      // Create assistant message placeholder
      const assistantMessage = createMessage('', 'assistant');
      assistantMessage.isStreaming = true;
      
      updateConversation(conversation.id, {
        messages: [...conversation.messages, userMessage, assistantMessage],
      });

      // Stream response
      let fullContent = '';
      await chatAPI.streamMessage(
        [...conversation.messages, userMessage],
        {
          model: process.env.REACT_APP_DEFAULT_MODEL || 'qwen/qwen3-4b',
          provider: (process.env.REACT_APP_DEFAULT_PROVIDER || 'llamacpp') as any,
          temperature: parseFloat(process.env.REACT_APP_DEFAULT_TEMPERATURE || '0.7'),
          max_tokens: parseInt(process.env.REACT_APP_DEFAULT_MAX_TOKENS || '2048'),
        },
        (chunk) => {
          fullContent += chunk;
          setState(prev => {
            const conv = prev.conversations.find(c => c.id === conversation!.id);
            if (!conv) return prev;

            const messages = [...conv.messages];
            const lastMessage = messages[messages.length - 1];
            if (lastMessage && lastMessage.id === assistantMessage.id) {
              lastMessage.content = fullContent;
            }

            return {
              ...prev,
              conversations: prev.conversations.map(c =>
                c.id === conversation!.id ? { ...c, messages } : c
              ),
            };
          });
        },
        (error) => {
          throw error;
        }
      );

      // Mark streaming as complete
      setState(prev => {
        const conv = prev.conversations.find(c => c.id === conversation!.id);
        if (!conv) return prev;

        const messages = [...conv.messages];
        const lastMessage = messages[messages.length - 1];
        if (lastMessage && lastMessage.id === assistantMessage.id) {
          lastMessage.isStreaming = false;
        }

        return {
          ...prev,
          conversations: prev.conversations.map(c =>
            c.id === conversation!.id ? { ...c, messages } : c
          ),
        };
      });

    } catch (error: any) {
      console.error('Error sending message:', error);
      setState(prev => ({ ...prev, error: error.message }));
      toast.error('Failed to send message');
    } finally {
      setState(prev => ({ ...prev, isLoading: false }));
    }
  }, [getCurrentConversation, updateConversation]);

  const regenerateLastMessage = useCallback(async () => {
    const conversation = getCurrentConversation();
    if (!conversation || conversation.messages.length < 2) return;

    // Remove last assistant message
    const messages = conversation.messages.slice(0, -1);
    updateConversation(conversation.id, { messages });

    // Get last user message and resend
    const lastUserMessage = messages[messages.length - 1];
    if (lastUserMessage && lastUserMessage.role === 'user') {
      await sendMessage(lastUserMessage.content);
    }
  }, [getCurrentConversation, updateConversation, sendMessage]);

  const createNewConversation = useCallback(() => {
    const conversation = createConversation();
    setState(prev => ({
      ...prev,
      conversations: [...prev.conversations, conversation],
      currentConversationId: conversation.id,
    }));
  }, []);

  const switchConversation = useCallback((id: string) => {
    setState(prev => ({ ...prev, currentConversationId: id }));
  }, []);

  const deleteConversation = useCallback((id: string) => {
    setState(prev => {
      const filtered = prev.conversations.filter(c => c.id !== id);
      const newCurrentId = prev.currentConversationId === id
        ? (filtered.length > 0 ? filtered[0].id : null)
        : prev.currentConversationId;

      return {
        ...prev,
        conversations: filtered,
        currentConversationId: newCurrentId,
      };
    });
    toast.success('Conversation deleted');
  }, []);

  const renameConversation = useCallback((id: string, title: string) => {
    updateConversation(id, { title });
  }, [updateConversation]);

  const clearConversations = useCallback(() => {
    setState(prev => ({
      ...prev,
      conversations: [],
      currentConversationId: null,
    }));
    storage.clearAll();
    toast.success('All conversations cleared');
  }, []);

  const value: ChatContextType = {
    ...state,
    sendMessage,
    regenerateLastMessage,
    createNewConversation,
    switchConversation,
    deleteConversation,
    renameConversation,
    clearConversations,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};