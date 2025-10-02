# debate_partner

An LLM partner catered specifically for the purpose of engaging in fair, beneficial, but heated debate.
Project: “AI Debate Partner”
Goal: Scaffold a full stack that matches this spec (backend + frontend + eval).

Functional pillars

Debate engine that opposes user stance on chosen topic, resists sycophancy, grounds claims, and avoids fallacies.

Rubric feedback (AQS 1–5: clarity, evidence, logic, rebuttal strength) + hallucination checks + opposition consistency tracking.

Topic constraints, retrieval grounding, uncertainty markers.

Tech choices

Backend: Python FastAPI; endpoints: /debate/start, /debate/respond, /evaluate, /health.

Retrieval: local vector store (FAISS), docs in data/corpora/\*; embed with sentence-transformers.

LLM calls: abstracted in app/llm.py so we can swap providers. Add anti-sycophancy system prompts.

Frontend: Next.js + Tailwind; pages for Topic Select → Live Debate → Feedback Summary.

Storage: SQLite for sessions & metrics via SQLAlchemy; simple for now.

Testing: pytest backend; Playwright smoke test frontend.

CI: GitHub Actions to run pytest and npm test.

Deliverables to generate now

File tree (exact) and minimal working stubs:

ai-debate-partner/
├─ README.md
├─ .gitignore
├─ docker-compose.yml
├─ backend/
│ ├─ app/
│ │ ├─ main.py
│ │ ├─ schemas.py
│ │ ├─ debate.py
│ │ ├─ evaluation.py
│ │ ├─ retrieval.py
│ │ ├─ llm.py
│ │ ├─ prompts/
│ │ │ ├─ system_antisycophancy.txt
│ │ │ ├─ system_factuality_guardrails.txt
│ │ └─ db.py
│ ├─ tests/
│ │ ├─ test_health.py
│ │ └─ test_evaluation.py
│ ├─ requirements.txt
│ └─ .env.example
├─ frontend/
│ ├─ package.json
│ ├─ next.config.js
│ ├─ src/
│ │ ├─ pages/
│ │ │ ├─ index.tsx
│ │ │ ├─ debate.tsx
│ │ │ └─ summary.tsx
│ │ ├─ components/
│ │ │ ├─ TopicPicker.tsx
│ │ │ ├─ DebateChat.tsx
│ │ │ └─ FeedbackPanel.tsx
│ │ └─ lib/api.ts
│ └─ tests/
│ └─ smoke.spec.ts
└─ .github/workflows/ci.yml

Back end behavior:

/debate/start – POST topic & user stance → returns session_id + first AI counter-position.

/debate/respond – POST session_id + user_msg → returns AI response, hallucination_flags, opposition_consistent: bool.

/evaluate – POST session_id → returns AQS (1–5) with sub-scores and explanations, hallucination rate, opposition consistency %.

Retrieval pipeline that chunks docs in data/corpora/ and grounds claims.

evaluation.py with rubric and thresholds:

Poor: AQS < 3.0; Hallucination > 25%; Opposition < 60%

Okay: 3.0–3.5; 15–25%; 60–75%

Good: 3.6–4.2; 5–15%; 76–90%

Excellent: > 4.2; < 5%; > 90%

Front end:

Topic picker → start session → live threaded debate UI → summary with scores.

Show uncertainty markers on AI claims and tooltips for grounded citations.

DX:

backend/requirements.txt with FastAPI, uvicorn, SQLAlchemy, pydantic, sentence-transformers, faiss-cpu, pytest.

frontend/package.json with next, react, tailwind, axios, playwright.

docker-compose.yml to run both services.

.env.example keys and how to run.

Tests for health endpoint and evaluation scoring math.

CI GitHub Actions: install, lint, test both apps.
