import React, { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { 
  PaperAirplaneIcon, 
  PaperClipIcon, 
  MicrophoneIcon 
} from '@heroicons/react/24/outline';
import { classNames } from '../../utils/helpers';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSend, disabled = false }) => {
  const [message, setMessage] = useState('');
  const [rows, setRows] = useState(1);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const maxRows = 5;

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = 'auto';
    const scrollHeight = textarea.scrollHeight;
    const lineHeight = parseInt(getComputedStyle(textarea).lineHeight);
    const newRows = Math.min(Math.ceil(scrollHeight / lineHeight), maxRows);
    
    setRows(newRows);
    textarea.style.height = `${scrollHeight}px`;
  };

  const handleSubmit = () => {
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage('');
      setRows(1);
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    // Handle image paste in the future
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        e.preventDefault();
        // TODO: Handle image upload
        console.log('Image paste detected');
      }
    }
  };

  return (
    <div className="relative max-w-3xl mx-auto">
      <div className={classNames(
        'relative bg-background-tertiary rounded-xl border transition-colors',
        disabled ? 'border-border-primary opacity-50' : 'border-border-primary focus-within:border-border-secondary'
      )}>
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          placeholder="Ask anything..."
          disabled={disabled}
          rows={rows}
          className={classNames(
            'w-full resize-none bg-transparent px-4 py-3 pr-32',
            'text-text-primary placeholder-text-tertiary',
            'focus:outline-none',
            'scrollbar-thin scrollbar-thumb-border-primary'
          )}
          style={{
            minHeight: '48px',
            maxHeight: `${maxRows * 24}px`,
          }}
        />

        {/* Bottom toolbar */}
        <div className="absolute bottom-2 right-2 flex items-center gap-1">
          {/* File attachment */}
          <button
            className="p-2 rounded-lg hover:bg-background-quaternary transition-colors"
            title="Attach file"
            disabled={disabled}
          >
            <PaperClipIcon className="w-4 h-4 text-text-tertiary hover:text-text-secondary" />
          </button>

          {/* Voice input */}
          <button
            className="p-2 rounded-lg hover:bg-background-quaternary transition-colors"
            title="Voice input"
            disabled={disabled}
          >
            <MicrophoneIcon className="w-4 h-4 text-text-tertiary hover:text-text-secondary" />
          </button>

          {/* Send button */}
          {message.trim() && (
            <button
              onClick={handleSubmit}
              disabled={disabled}
              className={classNames(
                'p-2 rounded-lg transition-all',
                disabled
                  ? 'bg-background-quaternary text-text-tertiary cursor-not-allowed'
                  : 'bg-accent-primary hover:bg-accent-primary/90 text-white'
              )}
              title="Send message"
            >
              <PaperAirplaneIcon className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Character/token counter */}
      {message.length > 0 && (
        <div className="absolute -bottom-6 right-0 text-xs text-text-tertiary">
          {message.length} characters
        </div>
      )}
    </div>
  );
};