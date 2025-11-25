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

export default function SummaryPage() { // feedback summary page
  const router = useRouter();
  const { sessionId } = router.query;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);

  useEffect(() => {
    const run = async () => {
      // fetch evaluation data
      if (typeof sessionId !== 'string') return;
      setLoading(true);
      setError(null);
      try {
        const response = await evaluateSession(sessionId);
        // persist scores
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
    <main className="app-shell">
      <section className="panel panel-narrow">
        <header className="panel-header">
          <div>
            <p className="eyebrow">Feedback summary</p>
            <h1 style={{ margin: 0 }}>Session review</h1>
          </div>
          {typeof sessionId === 'string' && <p className="helper-text">ID: {sessionId}</p>}
        </header>

        {loading && <p className="helper-text">Loading evaluation…</p>}
        {error && <p className="alert alert--error">{error}</p>}

        {evaluation && (
          <FeedbackPanel
            label={evaluation.label}
            aqs={evaluation.aqs_overall}
            scores={evaluation.scores}
            hallucinationRate={evaluation.hallucination_rate}
            oppositionConsistency={evaluation.opposition_consistency}
            notes={evaluation.notes}
            actions={
              <Link className="button button-secondary" href={{ pathname: '/debate', query: { sessionId } }}>
                Return to debate
              </Link>
            }
          />
        )}

        <Link className="link-inline" href="/">
          Start a new session
        </Link>
      </section>
    </main>
  );
}
