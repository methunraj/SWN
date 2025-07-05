import { v4 as uuidv4 } from 'uuid';
import { Message, Conversation } from '../types';

export const generateId = (): string => uuidv4();

export const createMessage = (
  content: string, 
  role: 'user' | 'assistant' | 'system' = 'user'
): Message => ({
  id: generateId(),
  content,
  role,
  timestamp: new Date(),
  isStreaming: false,
});

export const createConversation = (title: string = 'New Chat'): Conversation => ({
  id: generateId(),
  title,
  messages: [],
  createdAt: new Date(),
  updatedAt: new Date(),
});

export const scrollToBottom = (element: HTMLElement | null, smooth = true) => {
  if (!element) return;
  
  element.scrollTo({
    top: element.scrollHeight,
    behavior: smooth ? 'smooth' : 'auto',
  });
};

export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (error) {
    console.error('Failed to copy:', error);
    return false;
  }
};

export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  delay: number
): ((...args: Parameters<T>) => void) => {
  let timeoutId: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
};

export const classNames = (...classes: (string | boolean | undefined | null)[]): string => {
  return classes.filter(Boolean).join(' ');
};

export const generateConversationTitle = (firstMessage: string): string => {
  // Remove markdown formatting
  const cleanText = firstMessage
    .replace(/[#*`_~\[\]()]/g, '')
    .replace(/\n+/g, ' ')
    .trim();
  
  // Truncate to 50 characters
  return cleanText.length > 50 ? cleanText.substring(0, 47) + '...' : cleanText;
};