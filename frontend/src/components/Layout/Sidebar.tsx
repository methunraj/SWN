import React, { useState, useMemo } from 'react';
import { 
  PlusIcon, 
  MagnifyingGlassIcon, 
  XMarkIcon,
  Cog6ToothIcon,
  ChatBubbleLeftIcon,
  TrashIcon,
  PencilIcon
} from '@heroicons/react/24/outline';
import { useChat } from '../../contexts/ChatContext';
import { formatTimestamp, truncateText } from '../../utils/formatters';
import { classNames } from '../../utils/helpers';
import { Conversation } from '../../types';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState('');
  
  const { 
    conversations, 
    currentConversationId, 
    createNewConversation,
    switchConversation,
    deleteConversation,
    renameConversation
  } = useChat();

  const filteredConversations = useMemo(() => {
    if (!searchQuery.trim()) return conversations;
    
    const query = searchQuery.toLowerCase();
    return conversations.filter(conv => 
      conv.title.toLowerCase().includes(query) ||
      conv.messages.some(msg => msg.content.toLowerCase().includes(query))
    );
  }, [conversations, searchQuery]);

  const handleNewChat = () => {
    createNewConversation();
  };

  const handleStartEdit = (conversation: Conversation, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingId(conversation.id);
    setEditingTitle(conversation.title);
  };

  const handleSaveEdit = () => {
    if (editingId && editingTitle.trim()) {
      renameConversation(editingId, editingTitle.trim());
    }
    setEditingId(null);
    setEditingTitle('');
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingTitle('');
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      deleteConversation(id);
    }
  };

  if (!isOpen) {
    return (
      <div className="w-16 bg-background-secondary flex flex-col items-center py-4">
        <button
          onClick={onToggle}
          className="p-3 rounded-lg hover:bg-background-tertiary transition-colors"
        >
          <ChatBubbleLeftIcon className="w-5 h-5 text-text-secondary" />
        </button>
      </div>
    );
  }

  return (
    <div className="w-64 bg-background-secondary flex flex-col h-full">
      {/* Header */}
      <div className="p-4">
        <h1 className="text-xl font-semibold text-text-primary mb-4 gradient-text">
          Swift Neethi AI
        </h1>

        {/* New Chat Button */}
        <button
          onClick={handleNewChat}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                     border border-border-primary hover:bg-background-tertiary
                     transition-colors group"
        >
          <PlusIcon className="w-4 h-4 text-text-secondary group-hover:text-text-primary" />
          <span className="text-sm text-text-secondary group-hover:text-text-primary">
            New Chat
          </span>
        </button>

        {/* Search Input */}
        <div className="mt-4 relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-tertiary" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search conversations..."
            className="w-full pl-9 pr-9 py-2 bg-background-tertiary rounded-lg
                       text-sm text-text-primary placeholder-text-tertiary
                       border border-transparent focus:border-border-secondary
                       focus:outline-none transition-colors"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <XMarkIcon className="w-4 h-4 text-text-tertiary hover:text-text-secondary" />
            </button>
          )}
        </div>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2">
        {filteredConversations.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-text-tertiary text-sm">
              {searchQuery ? 'No conversations found' : 'No conversations yet'}
            </p>
          </div>
        ) : (
          <div className="space-y-1">
            {filteredConversations.map((conversation) => (
              <div
                key={conversation.id}
                onClick={() => switchConversation(conversation.id)}
                className={classNames(
                  'group relative px-3 py-3 rounded-lg cursor-pointer transition-all',
                  'hover:bg-background-tertiary',
                  currentConversationId === conversation.id && 
                  'bg-background-tertiary border-l-2 border-accent-primary'
                )}
              >
                {editingId === conversation.id ? (
                  <div className="flex items-center gap-2">
                    <input
                      type="text"
                      value={editingTitle}
                      onChange={(e) => setEditingTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleSaveEdit();
                        if (e.key === 'Escape') handleCancelEdit();
                      }}
                      onClick={(e) => e.stopPropagation()}
                      className="flex-1 px-2 py-1 bg-background-primary rounded
                                 text-sm text-text-primary focus:outline-none"
                      autoFocus
                    />
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSaveEdit();
                      }}
                      className="text-accent-primary hover:text-accent-primary/80"
                    >
                      ✓
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCancelEdit();
                      }}
                      className="text-text-tertiary hover:text-text-secondary"
                    >
                      ✕
                    </button>
                  </div>
                ) : (
                  <>
                    <h3 className="text-sm font-medium text-text-primary line-clamp-1">
                      {conversation.title}
                    </h3>
                    {conversation.messages.length > 0 && (
                      <p className="text-xs text-text-tertiary mt-1 line-clamp-2">
                        {truncateText(
                          conversation.messages[conversation.messages.length - 1].content,
                          50
                        )}
                      </p>
                    )}
                    <span className="text-xs text-text-tertiary mt-1 block">
                      {formatTimestamp(conversation.updatedAt)}
                    </span>

                    {/* Action buttons */}
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 
                                    opacity-0 group-hover:opacity-100 transition-opacity
                                    flex items-center gap-1">
                      <button
                        onClick={(e) => handleStartEdit(conversation, e)}
                        className="p-1 rounded hover:bg-background-quaternary"
                      >
                        <PencilIcon className="w-3 h-3 text-text-tertiary" />
                      </button>
                      <button
                        onClick={(e) => handleDelete(conversation.id, e)}
                        className="p-1 rounded hover:bg-background-quaternary"
                      >
                        <TrashIcon className="w-3 h-3 text-text-tertiary hover:text-red-500" />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Section */}
      <div className="p-4 border-t border-border-primary">
        <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg
                           hover:bg-background-tertiary transition-colors group">
          <Cog6ToothIcon className="w-4 h-4 text-text-tertiary group-hover:text-text-secondary" />
          <span className="text-sm text-text-tertiary group-hover:text-text-secondary">
            Settings
          </span>
        </button>
      </div>
    </div>
  );
};