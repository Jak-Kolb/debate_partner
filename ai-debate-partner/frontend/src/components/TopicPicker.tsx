// Collects a topic and user stance before creating a new session.
import { FormEvent, useState } from 'react';

type TopicPickerProps = {
  onStart: (topic: string, stance: string) => Promise<void> | void;
  loading?: boolean;
};

export function TopicPicker({ onStart, loading = false }: TopicPickerProps) {
  const [topic, setTopic] = useState('');
  const [stance, setStance] = useState('');

  const handleSubmit = async (event: FormEvent) => {
    // Avoid page reloads and skip empty submissions.
    event.preventDefault();
    if (!topic || !stance) return;
    await onStart(topic, stance);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 max-w-xl mx-auto">
      <div>
        <label className="block text-sm font-medium">Topic</label>
        <input
          className="w-full border rounded px-3 py-2"
          placeholder="e.g., Universal Basic Income"
          value={topic}
          onChange={(event) => setTopic(event.target.value)}
        />
      </div>
      <div>
        <label className="block text-sm font-medium">Your stance</label>
        <input
          className="w-full border rounded px-3 py-2"
          placeholder="State your position that the AI should oppose"
          value={stance}
          onChange={(event) => setStance(event.target.value)}
        />
      </div>
      <button
        className="w-full rounded bg-slate-900 text-white py-2 font-semibold disabled:opacity-50"
        disabled={loading}
        type="submit"
      >
        {loading ? 'Starting debate…' : 'Start debate'}
      </button>
    </form>
  );
}
