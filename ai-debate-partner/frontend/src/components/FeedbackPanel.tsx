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

export function FeedbackPanel({
  label,
  aqs,
  scores,
  hallucinationRate,
  oppositionConsistency,
  notes,
  actions,
}: FeedbackPanelProps) {
  return (
    <section className="border rounded p-4 space-y-3 bg-white shadow-sm">
      <header className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Rubric Feedback</h2>
          <p className="text-sm text-slate-600">Overall rating: {label}</p>
        </div>
        <span className="text-2xl font-bold">{aqs.toFixed(2)}</span>
      </header>

      <div className="grid grid-cols-2 gap-3 text-sm">
        {Object.entries(scores).map(([dimension, value]) => (
          <div key={dimension} className="rounded border px-3 py-2">
            <p className="font-semibold capitalize">{dimension}</p>
            <p className="text-slate-600">{value.toFixed(2)} / 5</p>
          </div>
        ))}
      </div>

      <div className="text-sm space-y-1">
        <p>Hallucination rate: {hallucinationRate.toFixed(2)}%</p>
        <p>Opposition consistency: {oppositionConsistency.toFixed(2)}%</p>
      </div>

      {notes && <p className="text-sm text-slate-700">{notes}</p>}

      {actions && <div className="pt-2">{actions}</div>}
    </section>
  );
}
