import { useRouter } from 'next/router';
import { useState } from 'react';

import { TopicPicker } from '../components/TopicPicker';
import { startDebate } from '../lib/api';

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStart = async (topic: string, stance: string) => {
    setLoading(true);
    setError(null);
    try {
      const response = await startDebate({ topic, stance });
      if (typeof window !== 'undefined') {
        window.sessionStorage.setItem(
          `debate-${response.session_id}`,
          JSON.stringify({
            sessionId: response.session_id,
            topic,
            stance,
            initialTurn: {
              role: 'assistant',
              content: response.ai_message,
              citations: response.citations,
              hallucinationFlags: response.hallucination_flags,
              oppositionConsistent: response.opposition_consistent,
            },
          })
        );
      }
      router.push({ pathname: '/debate', query: { sessionId: response.session_id } });
    } catch (err) {
      setError('Unable to start debate. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-100 py-16 px-6">
      <section className="max-w-3xl mx-auto space-y-6">
        <header className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">AI Debate Partner</h1>
          <p className="text-slate-600">
            Select a topic, share your stance, and receive grounded opposition with rubric feedback.
          </p>
        </header>
        {error && <p className="text-sm text-red-600 text-center">{error}</p>}
        <TopicPicker onStart={handleStart} loading={loading} />
      </section>
    </main>
  );
}
