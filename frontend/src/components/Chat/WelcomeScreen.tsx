import React from 'react';
import { 
  AcademicCapIcon, 
  CodeBracketIcon, 
  PencilIcon, 
  ChartBarIcon 
} from '@heroicons/react/24/outline';
import { EXAMPLE_PROMPTS } from '../../utils/constants';

interface WelcomeScreenProps {
  onPromptSelect: (prompt: string) => void;
}

const iconMap: { [key: string]: React.ComponentType<{ className?: string }> } = {
  'academic-cap': AcademicCapIcon,
  'code-bracket': CodeBracketIcon,
  'pencil': PencilIcon,
  'chart-bar': ChartBarIcon,
};

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onPromptSelect }) => {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8">
      <div className="max-w-2xl w-full text-center">
        {/* Logo/Icon */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-2">Swift Neethi AI</h1>
          <p className="text-text-secondary">How can I help you today?</p>
        </div>

        {/* Example Prompts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-12">
          {EXAMPLE_PROMPTS.map((prompt, index) => {
            const Icon = iconMap[prompt.icon] || CodeBracketIcon;
            
            return (
              <button
                key={index}
                onClick={() => onPromptSelect(prompt.prompt)}
                className="group p-4 bg-background-secondary rounded-lg border border-border-primary
                           hover:border-border-secondary hover:bg-background-tertiary
                           transition-all duration-200 text-left"
              >
                <div className="flex items-start gap-3">
                  <Icon className="w-5 h-5 text-text-tertiary group-hover:text-text-secondary mt-0.5" />
                  <div>
                    <h3 className="text-sm font-medium text-text-primary mb-1">
                      {prompt.title}
                    </h3>
                    <p className="text-xs text-text-tertiary group-hover:text-text-secondary">
                      {prompt.prompt}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Capabilities */}
        <div className="mt-16 text-sm text-text-tertiary">
          <p>Powered by local LLMs via Ollama and llama.cpp</p>
          <p className="mt-2">
            Ask me anything - from coding help to creative writing, analysis, and more.
          </p>
        </div>
      </div>
    </div>
  );
};