import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000',
});

export interface DebateTurn {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
}

export interface StartDebatePayload {
  topic: string;
  stance: string;
}

export async function startDebate(payload: StartDebatePayload) {
  const response = await api.post('/debate/start', payload);
  return response.data;
}

export async function sendDebateMessage(sessionId: string, userMessage: string) {
  const response = await api.post('/debate/respond', {
    session_id: sessionId,
    user_message: userMessage,
  });
  return response.data;
}

export async function evaluateSession(sessionId: string) {
  const response = await api.post('/evaluate', { session_id: sessionId });
  return response.data;
}
