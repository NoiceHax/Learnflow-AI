<div align="center">

# Astra
### AI Learning Platform for JEE Advanced

**Adaptive learning paths · Concept-level mastery · Socratic AI tutor**

[![Next.js](https://img.shields.io/badge/Next.js_15-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-8E75B2?style=flat-square&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

</div>

---

Astra is a production-quality AI learning platform for Grade 12 students preparing for JEE Advanced, covering Organic Chemistry, Inorganic Chemistry, Advanced Physics, and Advanced Mathematics.

It builds a personalised learning path from an initial assessment, teaches with premium lesson material, sharpens weak spots with adaptive quizzes, and offers **Ask Socrates** — an AI tutor that guides with questions instead of handing over answers.

---

## How It Works

Sign up → take an initial assessment → Astra builds your knowledge profile. From there, the dashboard becomes your command center: it surfaces what to study next, what's blocking your progress, and what you've forgotten and need to revisit. You never hand-build your path — the system decides based on where you actually are, not where the syllabus says you should be.

---

## Key Features

**Adaptive Learning Engine** — Mastery is tracked per concept using Exponential Moving Averages. Strong performance unlocks harder material; poor performance surfaces easier questions and prerequisite concepts. ≥ 80% moves you forward, < 60% resurfaces the topic with extra practice.

**Recursive Remediation** — When a concept keeps failing, the prerequisite graph decomposes it into its foundations (e.g. *Gauss's Law → Electric Flux → Vector Area → Dot Product*) and recommends teaching those first.

**Ask Socrates** — A floating AI tutor on every lesson page, aware of the subject, chapter, and content on screen. It never reveals the answer — it asks one leading question at a time and guides you to the insight yourself. Powered by Gemini 2.5 Flash with a built-in fallback if no key is set.

**Adaptive Quiz Engine** — Supports single correct, multiple correct, integer, and numerical question types with a timer, mark-for-review, and instant evaluation. Powers both the initial assessment and chapter practice.

**Spaced Repetition** — Concepts you've learned are resurfaced at calibrated intervals before you forget them.

**Premium Lesson Library** — 31 premium lessons across all four subjects, tightly coupled to the concept graph.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, TailwindCSS, shadcn/ui, Recharts |
| Backend | FastAPI, SQLAlchemy |
| Database | SQLite (default) · Supabase PostgreSQL via `DATABASE_URL` |
| Auth | JWT (email + password) |
| AI | Gemini 2.5 Flash · built-in Socratic fallback |

The app runs fully offline with zero external setup. Add a Gemini key and/or a Supabase connection string to upgrade — no code changes required.

---

## Getting Started

Install dependencies for both the backend (Python 3.10+) and frontend (Node.js 18+), seed the database, and run both servers. The full setup instructions are in [`SETUP.md`](SETUP.md).

---

## Testing & CI

The adaptive engine — grading, mastery EMA, question selection and the
prerequisite-aware learning path — is covered by a backend test suite. The tests
run **fully offline** (AI calls are forced off and an in-memory SQLite database is
used), so no API keys, network or local `.db` file are needed.

```bash
cd backend
python -m venv .venv && . .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

GitHub Actions (`.github/workflows/ci.yml`) runs these tests and a frontend
type-check + build on every push and pull request.

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

<div align="center">
<i>Built for students who don't leave anything on the table.</i>
</div>
