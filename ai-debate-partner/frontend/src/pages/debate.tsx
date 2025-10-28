// Live debate surface that streams turns and tracks session state.
import Link from 'next/link';
import { useRouter } from 'next/router';
import { useEffect, useMemo, useState } from 'react';

import { DebateChat } from '../components/DebateChat';
import { sendDebateMessage } from '../lib/api';

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

export default function DebatePage() {
  const router = useRouter();
  const { sessionId } = router.query;
  const [metadata, setMetadata] = useState<StoredSession | null>(null);
  const [transcript, setTranscript] = useState<TranscriptItem[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    // Restore the first assistant message and metadata from sessionStorage.
    if (typeof window === 'undefined' || typeof sessionId !== 'string') return;
    const raw = window.sessionStorage.getItem(`debate-${sessionId}`);
    if (!raw) return;
    const stored: StoredSession = JSON.parse(raw);
    setMetadata(stored);
    setTranscript([stored.initialTurn]);
  }, [sessionId]);

  const title = useMemo(() => {
    if (!metadata) return 'Debate';
    return `${metadata.topic} — opposing ${metadata.stance}`;
  }, [metadata]);

  const handleSend = async (message: string) => {
    // Optimistically append the user turn so the UI feels responsive.
    if (typeof sessionId !== 'string') return;
    setBusy(true);
    setTranscript((current) => [
      ...current,
      { role: 'user', content: message },
    ]);

    try {
      const response = await sendDebateMessage(sessionId, message);
      // Append the assistant reply once the backend responds.
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

  if (typeof sessionId !== 'string') {
    // The router has not hydrated yet; show a placeholder until it does.
    return <p className="p-6">Loading session…</p>;
  }

  return (
    <main className="min-h-screen bg-slate-50 py-10 px-6">
      <section className="max-w-4xl mx-auto space-y-6">
        <header className="space-y-1">
          <h1 className="text-2xl font-bold">{title}</h1>
          <p className="text-sm text-slate-600">Session ID: {sessionId}</p>
        </header>

        <DebateChat sessionId={sessionId} transcript={transcript} onSend={handleSend} busy={busy} />

        <div className="flex justify-end gap-3">
          <Link
            className="rounded bg-emerald-600 text-white px-4 py-2 font-semibold"
            href={{ pathname: '/summary', query: { sessionId } }}
          >
            View feedback summary
          </Link>
        </div>
      </section>
    </main>
  );
}
