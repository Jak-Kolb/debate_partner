import Link from 'next/link';
import { useRouter } from 'next/router';
import { useEffect, useMemo, useState } from 'react';

import { DebateChat } from '../components/DebateChat';
import { sendDebateMessage, startDebate } from '../lib/api';

type TranscriptItem = {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  hallucinationFlags?: string[];
  oppositionConsistent?: boolean;
};

type StoredSession = {
  sessionId: string;
  topic: string;
  stance: string;
  initialTurn: TranscriptItem;
};

export default function DebatePage() { // live debate surface
  const router = useRouter();
  const { sessionId, topic } = router.query;
  const [metadata, setMetadata] = useState<StoredSession | null>(null);
  const [transcript, setTranscript] = useState<TranscriptItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [stanceInput, setStanceInput] = useState('');
  const [initializing, setInitializing] = useState(false);

  useEffect(() => {
    // restore first assistant message and metadata
    if (typeof window === 'undefined' || typeof sessionId !== 'string') return;
    const raw = window.sessionStorage.getItem(`debate-${sessionId}`);
    if (!raw) return;
    const stored: StoredSession = JSON.parse(raw);
    setMetadata(stored);
    setTranscript([stored.initialTurn]);
  }, [sessionId]);

  const title = useMemo(() => {
    if (metadata) return `${metadata.topic} — opposing ${metadata.stance}`;
    if (typeof topic === 'string') return `Debate: ${topic}`;
    return 'Debate';
  }, [metadata, topic]);

  const handleStartSession = async () => {
    if (typeof topic !== 'string' || !stanceInput.trim()) return;
    setInitializing(true);
    try {
      const response = await startDebate({ topic, stance: stanceInput });
      const initialTurn: TranscriptItem = {
        role: 'assistant',
        content: response.ai_message,
        citations: response.citations,
        hallucinationFlags: response.hallucination_flags,
        oppositionConsistent: response.opposition_consistent,
      };
      
      const sessionData: StoredSession = {
        sessionId: response.session_id,
        topic,
        stance: stanceInput,
        initialTurn,
      };

      if (typeof window !== 'undefined') {
        window.sessionStorage.setItem(
          `debate-${response.session_id}`,
          JSON.stringify(sessionData)
        );
      }

      setMetadata(sessionData);
      setTranscript([initialTurn]);
      
      // update url without reloading
      router.replace({
        pathname: '/debate',
        query: { sessionId: response.session_id },
      }, undefined, { shallow: true });

    } catch (error) {
      console.error('Failed to start debate', error);
    } finally {
      setInitializing(false);
    }
  };

  const handleSend = async (message: string) => {
    // optimistically append user turn
    const currentSessionId = metadata?.sessionId || (typeof sessionId === 'string' ? sessionId : null);
    if (!currentSessionId) return;
    
    setBusy(true);
    setTranscript((current) => [
      ...current,
      { role: 'user', content: message },
    ]);

    try {
      const response = await sendDebateMessage(currentSessionId, message);
      // append assistant reply
      setTranscript((current) => [
        ...current,
        {
          role: 'assistant',
          content: response.ai_message,
          citations: response.citations,
          hallucinationFlags: response.hallucination_flags,
          oppositionConsistent: response.opposition_consistent,
        },
      ]);
    } catch (error) {
      console.error('Failed to send debate message', error);
    } finally {
      setBusy(false);
    }
  };

  if (!router.isReady) {
    return (
      <main className="app-shell">
        <p className="helper-text">Loading…</p>
      </main>
    );
  }

  // case 1: no session yet, ask for stance
  if (!metadata && typeof topic === 'string') {
    return (
      <main className="app-shell">
        <section className="panel panel-narrow">
          <header className="panel-header" style={{ marginBottom: '1.5rem' }}>
            <div>
              <p className="eyebrow">Opening statement</p>
              <h1 style={{ margin: 0 }}>{topic}</h1>
            </div>
          </header>

          <div className="form-grid">
            <label htmlFor="stance" className="helper-text">
              Briefly explain your take on this topic:
            </label>
            <textarea
              id="stance"
              className="textarea-field"
              placeholder="I believe that…"
              value={stanceInput}
              onChange={(e) => setStanceInput(e.target.value)}
            />
          </div>

          <button
            className="button button-primary button-full"
            onClick={handleStartSession}
            disabled={initializing || !stanceInput.trim()}
            type="button"
          >
            {initializing ? 'Initializing debate…' : 'Begin debate'}
          </button>
        </section>
      </main>
    );
  }

  // case 2: session active
  if (metadata) {
    return (
      <main className="app-shell">
        <section className="debate-layout">
          <div className="panel">
            <header className="panel-header">
              <div>
                <p className="eyebrow">Debating now</p>
                <h1 style={{ margin: 0 }}>{title}</h1>
              </div>
            </header>
          </div>

          <DebateChat transcript={transcript} onSend={handleSend} busy={busy} />

          <div className="panel" style={{ textAlign: 'right' }}>
            <Link
              className="button button-secondary"
              href={{ pathname: '/summary', query: { sessionId: metadata.sessionId } }}
            >
              End debate &amp; view feedback
            </Link>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <p className="helper-text">Invalid session state. Please return home.</p>
    </main>
  );
}
