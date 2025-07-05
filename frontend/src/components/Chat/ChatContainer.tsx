import React, { useEffect, useRef } from 'react';
import { useChat } from '../../contexts/ChatContext';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { WelcomeScreen } from './WelcomeScreen';
import { ArrowDownIcon } from '@heroicons/react/24/outline';
import { classNames } from '../../utils/helpers';

export const ChatContainer: React.FC = () => {
  const { conversations, currentConversationId, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [showScrollButton, setShowScrollButton] = React.useState(false);

  const currentConversation = conversations.find(c => c.id === currentConversationId);
  const messages = currentConversation?.messages || [];

  const scrollToBottom = (smooth = true) => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: smooth ? 'smooth' : 'auto' 
    });
  };

  useEffect(() => {
    scrollToBottom(false);
  }, [currentConversationId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages.length]);

  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    
    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const isNearBottom = scrollHeight - scrollTop - clientHeight < 100;
    setShowScrollButton(!isNearBottom);
  };

  return (
    <div className="flex flex-col h-full bg-background-primary">
      {/* Header */}
      <header className="h-14 border-b border-border-primary flex items-center px-4">
        <h2 className="text-base font-medium text-text-primary">
          {currentConversation?.title || 'New Chat'}
        </h2>
      </header>

      {/* Messages Area */}
      <div 
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
      >
        {messages.length === 0 ? (
          <WelcomeScreen onPromptSelect={sendMessage} />
        ) : (
          <>
            <MessageList messages={messages} />
            <div ref={messagesEndRef} className="h-32" />
          </>
        )}
      </div>

      {/* Scroll to Bottom Button */}
      {showScrollButton && (
        <button
          onClick={() => scrollToBottom()}
          className={classNames(
            'absolute bottom-32 right-8 p-2 rounded-full',
            'bg-background-tertiary border border-border-primary',
            'hover:bg-background-quaternary transition-all',
            'shadow-lg animate-fade-in'
          )}
        >
          <ArrowDownIcon className="w-5 h-5 text-text-secondary" />
        </button>
      )}

      {/* Input Area */}
      <div className="border-t border-border-primary p-4">
        <MessageInput onSend={sendMessage} disabled={false} />
      </div>
    </div>
  );
};