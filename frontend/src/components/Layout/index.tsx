import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { ChatContainer } from '../Chat';
import { useChat } from '../../contexts/ChatContext';

export const Layout: React.FC = () => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const { currentConversationId } = useChat();

  return (
    <div className="flex h-screen bg-background-primary">
      <Sidebar isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
      
      <main className="flex-1 flex flex-col overflow-hidden">
        <ChatContainer />
      </main>
    </div>
  );
};