const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface CreateSessionRequest {
  config: {
    routing_pattern: string;
    models: Array<{
      provider: string;
      model_name: string;
      role?: string;
      system_prompt?: string;
      temperature?: number;
      max_tokens?: number;
    }>;
    coordinator_model_id?: string;
    cost_limit?: number;
  };
}

export const api = {
  async createSession(request: CreateSessionRequest) {
    const response = await fetch(`${API_URL}/api/sessions/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Failed to create session: ${response.statusText}`);
    }

    return response.json();
  },

  async getSessions() {
    const response = await fetch(`${API_URL}/api/sessions/`);

    if (!response.ok) {
      throw new Error(`Failed to get sessions: ${response.statusText}`);
    }

    return response.json();
  },

  async getSession(sessionId: string) {
    const response = await fetch(`${API_URL}/api/sessions/${sessionId}`);

    if (!response.ok) {
      throw new Error(`Failed to get session: ${response.statusText}`);
    }

    return response.json();
  },

  async getHistory(sessionId: string) {
    const response = await fetch(`${API_URL}/api/sessions/${sessionId}/history`);

    if (!response.ok) {
      throw new Error(`Failed to get history: ${response.statusText}`);
    }

    return response.json();
  },

  async exportSession(sessionId: string, format: 'json' | 'markdown') {
    const response = await fetch(`${API_URL}/api/sessions/${sessionId}/export/${format}`);

    if (!response.ok) {
      throw new Error(`Failed to export session: ${response.statusText}`);
    }

    return response.json();
  },

  async getInfo() {
    const response = await fetch(`${API_URL}/api/info`);

    if (!response.ok) {
      throw new Error(`Failed to get info: ${response.statusText}`);
    }

    return response.json();
  },
};
