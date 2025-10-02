import Link from 'next/link';
import { useRouter } from 'next/router';
import { useEffect, useState } from 'react';

import { FeedbackPanel } from '../components/FeedbackPanel';
import { evaluateSession } from '../lib/api';

type Evaluation = {
  session_id: string;
  aqs_overall: number;
  scores: Record<string, number>;
  hallucination_rate: number;
  opposition_consistency: number;
  label: string;
  notes?: string;
};

export default function SummaryPage() {
  const router = useRouter();
  const { sessionId } = router.query;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);

  useEffect(() => {
    const run = async () => {
      if (typeof sessionId !== 'string') return;
      setLoading(true);
      setError(null);
      try {
        const response = await evaluateSession(sessionId);
        setEvaluation(response);
      } catch (err) {
        console.error(err);
        setError('Unable to load evaluation.');
      } finally {
        setLoading(false);
      }
    };

    run();
  }, [sessionId]);

  return (
    <main className="min-h-screen bg-slate-100 py-12 px-6">
      <section className="max-w-3xl mx-auto space-y-6">
        <header className="space-y-1">
          <h1 className="text-2xl font-bold">Feedback summary</h1>
          {typeof sessionId === 'string' && (
            <p className="text-sm text-slate-600">Session ID: {sessionId}</p>
          )}
        </header>

        {loading && <p>Loading evaluation…</p>}
        {error && <p className="text-sm text-red-600">{error}</p>}

        {evaluation && (
          <FeedbackPanel
            label={evaluation.label}
            aqs={evaluation.aqs_overall}
            scores={evaluation.scores}
            hallucinationRate={evaluation.hallucination_rate}
            oppositionConsistency={evaluation.opposition_consistency}
            notes={evaluation.notes}
            actions={
              <Link className="text-sm text-blue-600 underline" href={{ pathname: '/debate', query: { sessionId } }}>
                Return to debate
              </Link>
            }
          />
        )}

        <Link className="text-sm text-blue-600 underline" href="/">
          Start a new session
        </Link>
      </section>
    </main>
  );
}
