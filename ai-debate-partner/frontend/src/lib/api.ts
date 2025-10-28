// HTTP helpers for talking to the FastAPI backend.
import axios from 'axios';

const api = axios.create({
  // In dev we default to the docker-compose port; override with NEXT_PUBLIC_API_BASE_URL.
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
  // Kick off a new debate session and receive the assistant opener.
  const response = await api.post('/debate/start', payload);
  return response.data;
}

export async function sendDebateMessage(sessionId: string, userMessage: string) {
  // Stream a user rebuttal to the backend and get the assistant response.
  const response = await api.post('/debate/respond', {
    session_id: sessionId,
    user_message: userMessage,
  });
  return response.data;
}

export async function evaluateSession(sessionId: string) {
  // Request rubric feedback for the given session.
  const response = await api.post('/evaluate', { session_id: sessionId });
  return response.data;
}
