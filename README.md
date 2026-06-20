# Astra: AI Learning Platform for JEE Advanced

Astra is a production-quality AI learning platform for Grade 12 students preparing for
**JEE Advanced**, covering Organic Chemistry, Inorganic Chemistry, Advanced Physics and
Advanced Mathematics. It builds a personalised learning path from an initial assessment,
teaches with premium lesson material, sharpens weak spots with adaptive quizzes, and offers
**Ask Socrates**, an AI tutor that guides with questions instead of handing over answers.

> The AI tutor is **Socrates**. In the product it is always surfaced as **"Ask Socrates"**.

---

## Tech stack

| Layer     | Technology |
|-----------|-----------|
| Frontend  | Next.js 15 (App Router), TypeScript, TailwindCSS, shadcn/ui, Recharts |
| Backend   | FastAPI, SQLAlchemy |
| Database  | SQLite by default · swappable to **Supabase PostgreSQL** via `DATABASE_URL` |
| Auth      | JWT (email + password) |
| AI        | **Gemini 2.5 Flash** (with a built-in Socratic fallback if no key is set) |

The app runs fully offline with zero external setup. Add a Gemini key and/or a Supabase
connection string to upgrade. No code changes required.

---

## Project layout

```
Learnflow-AI/
├── backend/                 FastAPI app
│   └── app/
│       ├── main.py          app entrypoint + router wiring
│       ├── models.py        SQLAlchemy schema (10 tables from the spec)
│       ├── routers/         auth, catalog, quiz, assessment, learning_path,
│       │                    lessons, mastery, dashboard, socrates
│       ├── services/        grading · selection (adaptive) · mastery (+concepts) ·
│       │                    concepts (prereq graph) · intelligence (command center) ·
│       │                    learning_path · gemini
│       └── seed/            real JEE catalog, 128-question bank, 31 premium lessons
└── frontend/                Next.js app
    ├── app/
    │   ├── (app)/           dashboard (command center), lessons, analytics
    │   └── exam/            immersive exam mode: assessment, quiz/[id]
    ├── middleware.ts        host-based routing for the exam.* subdomain
    ├── components/          quiz-engine, socrates-widget (floating), exam-shell,
    │                        charts, app-shell, shadcn/ui primitives
    └── lib/                 api client, auth context, types
```
---

### The core flow

```
Sign up → Initial Assessment (exam mode) → Knowledge Profile
        → Dashboard command center ⇄ Lessons ⇄ Practice (exam mode)
        → Diagnose → Fix foundations → Advance   (the system decides what's next)
```

The student never hand-builds a path. The **Dashboard is the command center**. It
surfaces what to continue, what's recommended next (prerequisite-aware), weak areas
ranked by how much they block, a spaced-repetition revision queue, recursive
remediation, and plain-language AI recommendations.

#### What's adaptive (V2)

- **Concept mastery (EMA)** is tracked per concept, not just per chapter.
- **Adaptive question engine**: poor performance leads to easier questions + prerequisite
  concepts; strong → harder, advanced, multi-concept. Plus spaced repetition,
  weak-concept reinforcement and concept-coverage balancing. Two students get
  different sequences.
- **Recursive curriculum**: when a concept keeps failing, the prerequisite graph
  decomposes it into fundamentals (e.g. *Gauss's Law → Electric Flux → Vector Area →
  Dot Product*) and recommends teaching those first, then climbing back up.
- **Contextual Socrates**: a floating tutor on every learning page that already
  knows your subject, chapter, formulas and examples on screen.
- **Analytics interpretations**: every metric comes with what to do next.

- **Reusable Quiz Engine** powers both the initial assessment and chapter quizzes
  (single/multiple correct, integer, numerical; timer, mark-for-review, palette, instant
  evaluation and weak-topic detection).
- **Adaptive mastery** updates after every quiz (EMA of performance); ≥80% moves you forward,
  <60% resurfaces the topic with extra practice.
- **Learning path** respects prerequisites (topological order); weak chapters come first,
  strong chapters can be skipped. Two students with different assessments get different paths.
- **Ask Socrates** never reveals the answer outright. It guides with one leading question at a
  time, keeps session history, and uses Gemini 2.5 Flash (or the built-in Socratic fallback) .    

---
