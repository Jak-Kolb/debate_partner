import { ReactNode } from 'react';

type FeedbackPanelProps = {
  label: string;
  aqs: number;
  scores: Record<string, number>;
  hallucinationRate: number;
  oppositionConsistency: number;
  notes?: string;
  actions?: ReactNode;
};

export function FeedbackPanel({ // displays rubric scores
  label,
  aqs,
  scores,
  hallucinationRate,
  oppositionConsistency,
  notes,
  actions,
}: FeedbackPanelProps) {
  return (
    <section className="panel">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Rubric feedback</p>
          <h2>{label}</h2>
          <p className="helper-text">Overall rating</p>
        </div>
        <div className="score-pill" aria-label="Adjusted quality score">
          <span className="score-pill__label">AQS</span>
          <span className="score-pill__value">{aqs.toFixed(2)}</span>
        </div>
      </header>

      <div className="metric-grid" role="list">
        {Object.entries(scores).map(([dimension, value]) => (
          <div key={dimension} className="metric-card" role="listitem">
            <div className="metric-card__header">
              <span className="capitalize">{dimension}</span>
              <span>{value.toFixed(2)} / 5</span>
            </div>
            <div className="metric-bar" aria-hidden>
              <span
                className="metric-bar__fill"
                style={{ width: `${Math.min(100, Math.max(0, (value / 5) * 100))}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="stat-grid">
        <div className="stat-card">
          <p className="helper-text">Hallucination rate</p>
          <strong>{hallucinationRate.toFixed(2)}%</strong>
        </div>
        <div className="stat-card">
          <p className="helper-text">Opposition consistency</p>
          <strong>{oppositionConsistency.toFixed(2)}%</strong>
        </div>
      </div>

      {notes && (
        <blockquote className="notes">
          {notes}
        </blockquote>
      )}

      {actions && <div className="panel-footer">{actions}</div>}
    </section>
  );
}
