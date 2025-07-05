import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { 
  ClipboardDocumentIcon, 
  ArrowPathIcon,
  PencilIcon,
  HandThumbUpIcon,
  HandThumbDownIcon
} from '@heroicons/react/24/outline';
import { Message as MessageType } from '../../types';
import { copyToClipboard, classNames } from '../../utils/helpers';
import { useChat } from '../../contexts/ChatContext';
import toast from 'react-hot-toast';

interface MessageProps {
  message: MessageType;
}

export const Message: React.FC<MessageProps> = ({ message }) => {
  const { regenerateLastMessage } = useChat();
  const [copied, setCopied] = useState(false);
  const [hovering, setHovering] = useState(false);

  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  const handleCopy = async () => {
    const success = await copyToClipboard(message.content);
    if (success) {
      setCopied(true);
      toast.success('Copied to clipboard');
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRegenerate = () => {
    regenerateLastMessage();
  };

  const Avatar = () => (
    <div className={classNames(
      'w-8 h-8 rounded-md flex items-center justify-center text-white font-medium text-sm',
      isUser ? 'bg-gradient-to-br from-accent-user to-accent-primary' : 'bg-accent-ai'
    )}>
      {isUser ? 'U' : 'AI'}
    </div>
  );

  return (
    <div 
      className={classNames(
        'group px-4 py-4 hover:bg-white/[0.02] transition-colors message-fade-in',
        isUser && 'bg-background-primary',
        isAssistant && 'bg-background-primary/50'
      )}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      <div className="max-w-3xl mx-auto">
        <div className="flex gap-4">
          <Avatar />
          
          <div className="flex-1 overflow-hidden">
            {message.isStreaming && !message.content ? (
              <div className="flex items-center gap-2 text-text-secondary">
                <div className="flex gap-1">
                  <span className="animate-pulse-subtle">●</span>
                  <span className="animate-pulse-subtle" style={{ animationDelay: '0.2s' }}>●</span>
                  <span className="animate-pulse-subtle" style={{ animationDelay: '0.4s' }}>●</span>
                </div>
                <span className="text-sm">AI is thinking...</span>
              </div>
            ) : (
              <div className="prose prose-invert max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, className, children, ...props }: any) {
                      const match = /language-(\w+)/.exec(className || '');
                      const language = match ? match[1] : '';
                      const inline = node?.position ? false : true;
                      
                      if (!inline && language) {
                        return (
                          <div className="relative group/code">
                            <button
                              onClick={() => copyToClipboard(String(children))}
                              className="absolute right-2 top-2 p-1.5 rounded bg-background-quaternary
                                         opacity-0 group-hover/code:opacity-100 transition-opacity"
                              title="Copy code"
                            >
                              <ClipboardDocumentIcon className="w-4 h-4 text-text-secondary" />
                            </button>
                            <SyntaxHighlighter
                              style={vscDarkPlus as any}
                              language={language}
                              PreTag="div"
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          </div>
                        );
                      }
                      
                      return (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                    a({ href, children }) {
                      return (
                        <a 
                          href={href} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-accent-primary hover:underline"
                        >
                          {children}
                        </a>
                      );
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
              </div>
            )}

            {/* Message actions */}
            {hovering && !message.isStreaming && (
              <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={handleCopy}
                  className="p-1.5 rounded hover:bg-background-tertiary transition-colors"
                  title="Copy message"
                >
                  <ClipboardDocumentIcon className={classNames(
                    'w-4 h-4',
                    copied ? 'text-accent-primary' : 'text-text-tertiary'
                  )} />
                </button>

                {isAssistant && (
                  <>
                    <button
                      onClick={handleRegenerate}
                      className="p-1.5 rounded hover:bg-background-tertiary transition-colors"
                      title="Regenerate response"
                    >
                      <ArrowPathIcon className="w-4 h-4 text-text-tertiary" />
                    </button>
                    <button
                      className="p-1.5 rounded hover:bg-background-tertiary transition-colors"
                      title="Good response"
                    >
                      <HandThumbUpIcon className="w-4 h-4 text-text-tertiary" />
                    </button>
                    <button
                      className="p-1.5 rounded hover:bg-background-tertiary transition-colors"
                      title="Bad response"
                    >
                      <HandThumbDownIcon className="w-4 h-4 text-text-tertiary" />
                    </button>
                  </>
                )}

                {isUser && (
                  <button
                    className="p-1.5 rounded hover:bg-background-tertiary transition-colors"
                    title="Edit message"
                  >
                    <PencilIcon className="w-4 h-4 text-text-tertiary" />
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};