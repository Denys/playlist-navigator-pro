import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { GoogleGenAI } from '@google/genai';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
}

export function AssistantTab() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I am your Playlist Navigator AI Assistant. I have access to all your indexed playlists and videos. How can I help you today?',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatRef = useRef<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      if (!chatRef.current) {
        const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
        chatRef.current = ai.chats.create({
          model: 'gemini-3-flash-preview',
          config: {
            systemInstruction: 'You are an AI assistant for a YouTube Playlist Indexer application. You help users navigate their playlists, find videos, and summarize content.',
          },
        });
      }

      const response = await chatRef.current.sendMessage({ message: userMessage.content });
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.text || 'Sorry, I could not generate a response.',
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error calling Gemini API:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-12rem)] flex flex-col">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-600 to-sky-500 flex items-center justify-center shadow-lg shadow-emerald-600/20">
          <Bot size={24} className="text-white" />
        </div>
        <div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white">AI Assistant</h2>
          <p className="text-slate-500 dark:text-white/60">Your personal guide to your video library</p>
        </div>
      </div>

      <div className="flex-1 liquid-glass rounded-3xl p-6 flex flex-col shadow-2xl overflow-hidden">
        <div className="flex-1 overflow-y-auto pr-4 space-y-6 scrollbar-thin scrollbar-thumb-slate-300 dark:scrollbar-thumb-white/20 scrollbar-track-transparent">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                  msg.role === 'user'
                    ? 'bg-sky-500/20 text-sky-600 dark:text-sky-400 border border-sky-500/30'
                    : 'bg-emerald-600/20 text-emerald-700 dark:text-emerald-400 border border-emerald-600/30'
                }`}
              >
                {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
              </div>
              <div
                className={`max-w-[80%] rounded-2xl p-4 ${
                  msg.role === 'user'
                    ? 'bg-sky-500/20 border border-sky-500/30 text-slate-900 dark:text-white rounded-tr-none'
                    : 'liquid-glass-sm text-slate-800 dark:text-white/90 rounded-tl-none border-0'
                }`}
              >
                <p className="whitespace-pre-wrap leading-relaxed">{msg.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-4">
              <div className="w-10 h-10 rounded-full bg-emerald-600/20 text-emerald-700 dark:text-emerald-400 border border-emerald-600/30 flex items-center justify-center shrink-0">
                <Bot size={20} />
              </div>
              <div className="liquid-glass-sm rounded-2xl rounded-tl-none p-4 flex items-center gap-2 border-0">
                <Loader2 size={20} className="animate-spin text-emerald-700 dark:text-emerald-400" />
                <span className="text-slate-500 dark:text-white/60">Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="mt-6 relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything about your playlists..."
            className="w-full liquid-glass-sm border-0 rounded-2xl py-4 pl-6 pr-16 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-emerald-600/50"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 rounded-xl bg-gradient-to-r from-emerald-600 to-sky-500 flex items-center justify-center text-white shadow-lg hover:scale-105 transition-transform disabled:opacity-50 disabled:hover:scale-100"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
