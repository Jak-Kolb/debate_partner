// Renders the live debate transcript and message composer.
import { FormEvent, useMemo, useState } from 'react';

type TranscriptItem = {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
  hallucinationFlags?: string[];
  oppositionConsistent?: boolean;
};

type DebateChatProps = {
  sessionId: string;
  transcript: TranscriptItem[];
  onSend: (message: string) => Promise<void> | void;
  busy?: boolean;
};

export function DebateChat({ sessionId, transcript, onSend, busy = false }: DebateChatProps) {
  const [draft, setDraft] = useState('');

  const lastAssistant = useMemo(
    // Track the latest assistant turn so we can surface stance-drift warnings.
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
    <div className="space-y-4">
      <header className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Session {sessionId}</h2>
        {lastAssistant?.oppositionConsistent === false && (
          <span className="text-xs font-medium text-amber-600">Warning: stance drift detected</span>
        )}
      </header>

      <div className="border rounded p-4 space-y-3 max-h-96 overflow-y-auto">
        {/* Transcript area shows both user and assistant turns with lightweight cues. */}
        {transcript.map((item, index) => (
          <article
            key={`${item.role}-${index}`}
            className={item.role === 'assistant' ? 'text-slate-900' : 'text-slate-600'}
          >
            <p className="font-semibold capitalize">{item.role}</p>
            <p className="whitespace-pre-line text-sm leading-6">
              {item.content}
              {item.role === 'assistant' && !item.citations?.length && (
                <span className="ml-1 text-xs text-amber-600">[uncertain]</span>
              )}
            </p>
            {!!item.citations?.length && (
              <ul className="text-xs text-slate-500 list-disc pl-5">
                {item.citations.map((citation) => (
                  <li key={citation}>{citation}</li>
                ))}
              </ul>
            )}
            {!!item.hallucinationFlags?.length && (
              <p className="text-xs text-red-600">
                {item.hallucinationFlags.join(' ')}
              </p>
            )}
          </article>
        ))}
        {!transcript.length && <p className="text-sm text-slate-500">Waiting for the first response…</p>}
      </div>

      <form onSubmit={handleSubmit} className="space-y-2">
        {/* Simple textarea flow keeps the UX keyboard-friendly. */}
        <textarea
          className="w-full border rounded px-3 py-2"
          rows={3}
          placeholder="Challenge the assistant..."
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
        />
        <button
          className="rounded bg-blue-600 text-white px-4 py-2 font-semibold disabled:opacity-50"
          disabled={busy}
          type="submit"
        >
          {busy ? 'Sending…' : 'Send rebuttal'}
        </button>
      </form>
    </div>
  );
}
