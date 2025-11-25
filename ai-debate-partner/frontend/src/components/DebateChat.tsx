import { FormEvent, useMemo, useState } from 'react';

type TranscriptItem = {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  hallucinationFlags?: string[];
  oppositionConsistent?: boolean;
};

type DebateChatProps = {
  transcript: TranscriptItem[];
  onSend: (message: string) => Promise<void> | void;
  busy?: boolean;
};

export function DebateChat({ transcript, onSend, busy = false }: DebateChatProps) { // renders live debate transcript
  const [draft, setDraft] = useState('');

  const lastAssistant = useMemo(
    // track latest assistant turn
    () => transcript.filter((entry) => entry.role === 'assistant').slice(-1)[0],
    [transcript]
  );

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    if (!draft.trim()) return;
    await onSend(draft.trim());
    setDraft('');
  };

  return (
    <section className="panel">
      <header className="panel-header">
        <div>
          <p className="eyebrow">Active session</p>
          <h2>Debate Transcript</h2>
        </div>
        {lastAssistant?.oppositionConsistent === false && (
          <span className="warning-pill">Stance drift detected</span>
        )}
      </header>

      <div className="scroll-area transcript" aria-live="polite" aria-label="Debate transcript">
        {transcript.map((item, index) => (
          <article
            key={`${item.role}-${index}`}
            className={`transcript__item ${item.role === 'assistant' ? 'transcript__item--assistant' : ''}`}
          >
            <p className="transcript__item-role">{item.role}</p>
            <p className="whitespace-pre-line">
              {item.content}
              {item.role === 'assistant' && !item.citations?.length && (
                <span className="helper-text" style={{ marginLeft: '0.35rem' }}>[uncertain]</span>
              )}
            </p>
            {!!item.hallucinationFlags?.length && (
              <p className="helper-text" style={{ color: 'var(--danger)' }}>
                {item.hallucinationFlags.join(' ')}
              </p>
            )}
          </article>
        ))}
        {!transcript.length && (
          <p className="helper-text">Waiting for the first response…</p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="form-grid">
        <label htmlFor="debate-draft" className="visually-hidden">
          Compose rebuttal
        </label>
        <textarea
          id="debate-draft"
          className="textarea-field"
          rows={4}
          placeholder="Challenge the assistant..."
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
        />
        <div className="action-row">
          <span className="helper-text">Shift + Enter for a new line</span>
          <button className="button button-primary" disabled={busy} type="submit">
            {busy ? 'Sending…' : 'Send rebuttal'}
          </button>
        </div>
      </form>
    </section>
  );
}
