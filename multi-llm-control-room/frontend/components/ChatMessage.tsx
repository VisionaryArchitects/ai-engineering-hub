'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Message } from '@/lib/store';

interface ChatMessageProps {
  message: Message;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div
      className={`mb-6 p-4 rounded-lg ${
        isUser
          ? 'bg-blue-900/30 border-l-4 border-blue-500'
          : 'bg-gray-800/50 border-l-4 border-green-500'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm">
            {isUser ? '👤 You' : `🤖 ${message.model_id || 'Assistant'}`}
          </span>
          <span className="text-xs text-gray-400">
            {new Date(message.timestamp).toLocaleTimeString()}
          </span>
        </div>

        {!isUser && (message.tokens || message.cost !== undefined) && (
          <div className="flex gap-3 text-xs text-gray-400">
            {message.tokens && <span>📊 {message.tokens} tokens</span>}
            {message.cost !== undefined && (
              <span>💰 ${message.cost.toFixed(4)}</span>
            )}
          </div>
        )}
      </div>

      <div className="prose prose-invert prose-sm max-w-none">
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
    </div>
  );
};

export default ChatMessage;
