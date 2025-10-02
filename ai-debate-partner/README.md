# AI Debate Partner

Scaffolding for a debate partner that challenges the user, grounds arguments in a local corpus, and returns rubric-based feedback.

## Project Structure

- `backend/`: FastAPI application with retrieval, LLM abstraction, and evaluation logic.
- `frontend/`: Next.js app with Topic Select → Debate → Summary flow.
- `data/corpora/`: Place grounding documents here (not committed by default).
- `.github/workflows/ci.yml`: CI pipeline running backend and frontend tests.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker (optional for containerized dev)

### Environment

Copy the sample environment for the backend and adjust values as needed:

```bash
cp backend/.env.example backend/.env
```

Place source documents under `data/corpora/` for retrieval.

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker Compose

Run both services together:

```bash
docker-compose up --build
```

### Testing

- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npx playwright test`

## CI

GitHub Actions workflow installs dependencies and runs the backend and frontend test suites on push and pull requests.
