# AI Debate Partner

An LLM-powered debate partner designed to engage users in fair, beneficial, and heated debates. The system challenges the user's stance, resists sycophancy, grounds claims in evidence, and provides detailed feedback based on a debate rubric.

## Code Structure

The project is organized as a full-stack application with a Python backend and a TypeScript/React frontend.

### `backend/`

Built with **FastAPI**, this service handles the core debate logic, LLM interactions, and session management.

- **`app/main.py`**: Entry point for the API, defining endpoints for starting debates, responding, and evaluation.
- **`app/debate.py`**: Manages debate sessions, state persistence, and the orchestration of the debate flow.
- **`app/llm.py`**: Abstraction layer for LLM providers (e.g., OpenAI), handling prompt construction and generation.
- **`app/retrieval.py`**: Implements the RAG (Retrieval-Augmented Generation) pipeline using **FAISS** and **Sentence Transformers** to ground arguments in the provided corpora.
- **`app/evaluation.py`**: Contains the logic for scoring debates based on the Argument Quality Score (AQS) rubric, checking for hallucinations, and tracking opposition consistency.
- **`app/db.py`**: Database configuration using **SQLAlchemy** (defaults to SQLite).
- **`data/corpora/`**: Directory for text files used as the knowledge base for the debate partner.

### `frontend/`

Built with **Next.js** and **Tailwind CSS**, providing a responsive interface for the debate experience.

- **`src/pages/`**: Application routes (Topic Selection, Debate Interface, Summary/Feedback).
- **`src/components/`**: Reusable UI components like `DebateChat`, `TopicPicker`, and `FeedbackPanel`.
- **`src/lib/api.ts`**: API client for communicating with the backend.

## Dependencies

### Backend

- **FastAPI & Uvicorn**: Web framework and ASGI server.
- **SQLAlchemy**: ORM for database interactions.
- **OpenAI**: Client for LLM generation.
- **Sentence-Transformers & FAISS**: For embedding generation and vector similarity search.
- **Pydantic**: Data validation and settings management.

### Frontend

- **Next.js**: React framework for production.
- **React**: UI library.
- **Tailwind CSS**: Utility-first CSS framework for styling.
- **Axios**: HTTP client.

## Instructions to Run

**Backend:**

1. Navigate to `ai-debate-partner/backend`.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   or on Windows Powershell:

   ```bash
   python -m venv .venv
   .\\.venv\\Scripts\\Activate.ps1
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and add your `LLM_API_KEY` (e.g., OpenAI API key) to enable the debate partner functionality.
5. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```

**Frontend:**

1. Navigate to `ai-debate-partner/frontend`.
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```

## Attribution

This project consists of original code written for this assignment. LLMs were used in assistance, especially on the UI design.

It utilizes the following external libraries and frameworks:

- **FastAPI** and **Uvicorn** (Backend)
- **Next.js**, **React**, and **Tailwind CSS** (Frontend)
- **SQLAlchemy** (Database)
- **OpenAI** (LLM Integration)
