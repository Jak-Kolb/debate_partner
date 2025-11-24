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
    <form onSubmit={handleSubmit} className="form-grid topic-picker">
      <div className="form-grid">
        <label htmlFor="topic-input" className="helper-text">
          Topic
        </label>
        <input
          id="topic-input"
          className="input-field"
          placeholder="e.g., Universal Basic Income"
          value={topic}
          onChange={(event) => setTopic(event.target.value)}
        />
      </div>
      <div className="form-grid">
        <label htmlFor="stance-input" className="helper-text">
          Your stance
        </label>
        <input
          id="stance-input"
          className="input-field"
          placeholder="State your position that the AI should oppose"
          value={stance}
          onChange={(event) => setStance(event.target.value)}
        />
      </div>
      <button className="button button-primary button-full" disabled={loading} type="submit">
        {loading ? 'Starting debate…' : 'Start debate'}
      </button>
    </form>
  );
}
