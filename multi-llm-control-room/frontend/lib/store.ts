import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  model_id?: string;
  timestamp: string;
  tokens?: number;
  cost?: number;
}

export interface ModelConfig {
  id: string;
  provider: string;
  model_name: string;
  role?: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface Session {
  id?: string;
  routing_pattern: string;
  models: ModelConfig[];
  coordinator_model_id?: string;
  total_tokens: number;
  total_cost: number;
  status: 'idle' | 'active' | 'paused';
}

interface ChatStore {
  // Session state
  session: Session;
  messages: Message[];
  isConnected: boolean;
  isLoading: boolean;
  ws: WebSocket | null;

  // Actions
  setSession: (session: Session) => void;
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setConnected: (connected: boolean) => void;
  setLoading: (loading: boolean) => void;
  setWebSocket: (ws: WebSocket | null) => void;
  updateSessionStats: (tokens: number, cost: number) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  session: {
    routing_pattern: 'broadcast',
    models: [],
    total_tokens: 0,
    total_cost: 0,
    status: 'idle',
  },
  messages: [],
  isConnected: false,
  isLoading: false,
  ws: null,

  setSession: (session) => set({ session }),

  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  clearMessages: () => set({ messages: [] }),

  setConnected: (connected) => set({ isConnected: connected }),

  setLoading: (loading) => set({ isLoading: loading }),

  setWebSocket: (ws) => set({ ws }),

  updateSessionStats: (tokens, cost) =>
    set((state) => ({
      session: {
        ...state.session,
        total_tokens: state.session.total_tokens + tokens,
        total_cost: state.session.total_cost + cost,
      },
    })),
}));
