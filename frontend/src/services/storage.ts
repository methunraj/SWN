import { Conversation } from '../types';

const STORAGE_KEYS = {
  CONVERSATIONS: 'swift-neethi-conversations',
  CURRENT_CONVERSATION: 'swift-neethi-current-conversation',
  PREFERENCES: 'swift-neethi-preferences',
} as const;

export const storage = {
  // Conversations
  getConversations: (): Conversation[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Error loading conversations:', error);
      return [];
    }
  },

  saveConversations: (conversations: Conversation[]): void => {
    try {
      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
    } catch (error) {
      console.error('Error saving conversations:', error);
    }
  },

  getCurrentConversationId: (): string | null => {
    return localStorage.getItem(STORAGE_KEYS.CURRENT_CONVERSATION);
  },

  setCurrentConversationId: (id: string | null): void => {
    if (id) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_CONVERSATION, id);
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_CONVERSATION);
    }
  },

  // Preferences
  getPreferences: () => {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.PREFERENCES);
      return data ? JSON.parse(data) : {};
    } catch (error) {
      console.error('Error loading preferences:', error);
      return {};
    }
  },

  savePreferences: (preferences: any): void => {
    try {
      localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(preferences));
    } catch (error) {
      console.error('Error saving preferences:', error);
    }
  },

  // Clear all data
  clearAll: (): void => {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  },
};