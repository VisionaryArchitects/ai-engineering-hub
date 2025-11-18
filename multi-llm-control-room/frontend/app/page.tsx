'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useChatStore, ModelConfig, Message } from '@/lib/store';
import { api } from '@/lib/api';
import SessionSetup from '@/components/SessionSetup';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';

export default function Home() {
  const [sessionStarted, setSessionStarted] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    session,
    messages,
    isConnected,
    isLoading,
    ws,
    setSession,
    addMessage,
    clearMessages,
    setConnected,
    setLoading,
    setWebSocket,
    updateSessionStats,
  } = useChatStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const connectWebSocket = (sessionId: string) => {
    const socket = new WebSocket(`${WS_URL}/ws/${sessionId}`);

    socket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setLoading(false);
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'user_message') {
        // User message echoed back
        const msg: Message = {
          id: Date.now().toString(),
          role: 'user',
          content: data.content,
          timestamp: new Date().toISOString(),
        };
        addMessage(msg);
      } else if (data.type === 'model_response') {
        // Model response
        const msg: Message = {
          id: Date.now().toString() + '_' + data.model_id,
          role: 'assistant',
          content: data.content,
          model_id: data.model_id,
          timestamp: data.timestamp,
          tokens: data.tokens,
          cost: data.cost,
        };
        addMessage(msg);
        setLoading(false);
      } else if (data.type === 'response_complete') {
        // All models responded
        updateSessionStats(data.total_tokens, data.total_cost);
        setLoading(false);
      } else if (data.type === 'error') {
        console.error('WebSocket error:', data.message);
        alert(`Error: ${data.message}`);
        setLoading(false);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setConnected(false);
      setLoading(false);
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
      setLoading(false);
    };

    setWebSocket(socket);
  };

  const handleStartSession = async (routing: string, models: ModelConfig[]) => {
    try {
      setLoading(true);

      // Create session via API
      const sessionData = await api.createSession({
        config: {
          routing_pattern: routing,
          models: models.map((m) => ({
            provider: m.provider,
            model_name: m.model_name,
            role: m.role,
            temperature: m.temperature || 0.7,
          })),
        },
      });

      console.log('Session created:', sessionData);

      // Update store
      setSession({
        id: sessionData.id,
        routing_pattern: routing,
        models,
        total_tokens: 0,
        total_cost: 0,
        status: 'active',
      });

      // Connect WebSocket
      connectWebSocket(sessionData.id);

      setSessionStarted(true);
    } catch (error: any) {
      console.error('Failed to start session:', error);
      alert(`Failed to start session: ${error.message}`);
      setLoading(false);
    }
  };

  const handleSendMessage = (content: string) => {
    if (!ws || !isConnected) {
      alert('Not connected to session');
      return;
    }

    setLoading(true);

    ws.send(
      JSON.stringify({
        action: 'send_message',
        content,
        temperature: 0.7,
      })
    );
  };

  const handleExport = async (format: 'json' | 'markdown') => {
    if (!session.id) return;

    try {
      const data = await api.exportSession(session.id, format);

      if (format === 'json') {
        // Download JSON
        const blob = new Blob([JSON.stringify(data, null, 2)], {
          type: 'application/json',
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `session-${session.id}.json`;
        a.click();
      } else if (format === 'markdown') {
        // Download Markdown
        const blob = new Blob([data.content], { type: 'text/markdown' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `session-${session.id}.md`;
        a.click();
      }
    } catch (error: any) {
      alert(`Export failed: ${error.message}`);
    }
  };

  const handleReset = () => {
    if (ws) {
      ws.close();
    }
    setWebSocket(null);
    clearMessages();
    setSession({
      routing_pattern: 'broadcast',
      models: [],
      total_tokens: 0,
      total_cost: 0,
      status: 'idle',
    });
    setSessionStarted(false);
    setConnected(false);
  };

  if (!sessionStarted) {
    return (
      <main className="min-h-screen bg-gradient-to-b from-gray-900 to-black flex items-center justify-center p-6">
        <SessionSetup onStart={handleStartSession} />
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-black flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">🎛️ Multi-LLM Control Room</h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
              <span>
                {isConnected ? (
                  <span className="text-green-400">🟢 Connected</span>
                ) : (
                  <span className="text-red-400">🔴 Disconnected</span>
                )}
              </span>
              <span>Pattern: {session.routing_pattern}</span>
              <span>Models: {session.models.length}</span>
              <span>Tokens: {session.total_tokens}</span>
              <span>Cost: ${session.total_cost.toFixed(4)}</span>
            </div>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => handleExport('json')}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition text-sm"
            >
              Export JSON
            </button>
            <button
              onClick={() => handleExport('markdown')}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded transition text-sm"
            >
              Export MD
            </button>
            <button
              onClick={handleReset}
              className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded transition text-sm"
            >
              New Session
            </button>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="text-center text-gray-400 mt-20">
              <p className="text-xl mb-2">👋 Ready to collaborate!</p>
              <p>Send a message to start the multi-LLM conversation</p>
            </div>
          ) : (
            <>
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              <div ref={messagesEndRef} />
            </>
          )}

          {isLoading && (
            <div className="text-center text-gray-400 py-4">
              <span className="animate-pulse">🤖 Models are thinking...</span>
            </div>
          )}
        </div>
      </div>

      {/* Input Area */}
      <ChatInput onSend={handleSendMessage} disabled={isLoading || !isConnected} />
    </main>
  );
}
