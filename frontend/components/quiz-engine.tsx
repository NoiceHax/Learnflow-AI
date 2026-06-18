"use client";

import { useEffect, useMemo, useState } from "react";
import { Clock, Flag, ChevronLeft, ChevronRight, SkipForward, Loader2, CheckCircle2 } from "lucide-react";
import type { AnswerValue, Question } from "@/lib/types";

interface Props {
  questions: Question[];
  title: string;
  subtitle?: string;
  submitLabel?: string;
  submitting?: boolean;
  onSubmit: (answers: { question_id: string; answer: AnswerValue }[], timeTaken: number) => void;
}

const DIFF_COLOR: Record<string, string> = {
  Easy: "var(--success-clr)",
  Medium: "var(--warning-clr)",
  Hard: "var(--error-clr)",
  Advanced: "var(--error-clr)",
};

function Bar({ value }: { value: number }) {
  return (
    <div style={{ height: 4, background: "var(--surface-3)", borderRadius: 99, overflow: "hidden" }}>
      <div
        style={{
          width: `${value}%`,
          height: "100%",
          background: "var(--indigo)",
          borderRadius: 99,
          transition: "width 1s var(--ease)",
        }}
      />
    </div>
  );
}

export function QuizEngine({ questions, title, subtitle, submitLabel = "Submit", submitting, onSubmit }: Props) {
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, AnswerValue>>({});
  const [marked, setMarked] = useState<Set<string>>(new Set());
  const [seconds, setSeconds] = useState(0);
  const [reviewing, setReviewing] = useState(false);

  useEffect(() => {
    const t = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(t);
  }, []);

  const q = questions[index];
  const total = questions.length;

  const answeredCount = useMemo(
    () => questions.filter((qq) => isAnswered(answers[qq.id])).length,
    [answers, questions]
  );

  function setAnswer(value: AnswerValue) {
    setAnswers((prev) => ({ ...prev, [q.id]: value }));
  }

  function toggleMultiple(optIndex: number) {
    const current = Array.isArray(answers[q.id]) ? [...(answers[q.id] as number[])] : [];
    const pos = current.indexOf(optIndex);
    if (pos >= 0) current.splice(pos, 1);
    else current.push(optIndex);
    current.sort((a, b) => a - b);
    setAnswer(current.length ? current : null);
  }

  function toggleMark() {
    setMarked((prev) => {
      const next = new Set(prev);
      if (next.has(q.id)) next.delete(q.id);
      else next.add(q.id);
      return next;
    });
  }

  function go(to: number) {
    setIndex(Math.max(0, Math.min(total - 1, to)));
    setReviewing(false);
  }

  function handleSubmit() {
    const payload = questions.map((qq) => ({ question_id: qq.id, answer: answers[qq.id] ?? null }));
    onSubmit(payload, seconds);
  }

  const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
  const ss = String(seconds % 60).padStart(2, "0");

  return (
    <div className="exam-grid">
      <div>
        <div className="between" style={{ flexWrap: "wrap", gap: 12, marginBottom: 28 }}>
          <div>
            <h1 className="title">{title}</h1>
            {subtitle && <p className="faint body-sm" style={{ marginTop: 4 }}>{subtitle}</p>}
          </div>
          <div className="lf-row" style={{ gap: 8 }}>
            <Clock size={16} style={{ color: "var(--text-faint)" }} />
            <span className="lf-mono" style={{ fontSize: 17, fontWeight: 600 }}>
              {mm}:{ss}
            </span>
          </div>
        </div>

        {!reviewing ? (
          <div className="fade-in" key={q.id}>
            <div className="between" style={{ flexWrap: "wrap", gap: 10 }}>
              <div className="lf-label">
                Question {String(index + 1).padStart(2, "0")} / {String(total).padStart(2, "0")}
              </div>
              <div className="lf-row" style={{ gap: 8, flexWrap: "wrap" }}>
                <span className="chip" style={{ fontSize: 11 }}>
                  {q.concept.replace(/^\[AI\]\s*/, "")}
                </span>
                {q.ai_generated && (
                  <span className="chip" style={{ fontSize: 11, background: "var(--indigo-wash)", color: "var(--indigo-bright)" }}>
                    Fresh · AI
                  </span>
                )}
                <span className="chip" style={{ fontSize: 11, color: DIFF_COLOR[q.difficulty] || "var(--text-dim)" }}>
                  {q.difficulty}
                </span>
                <button
                  onClick={toggleMark}
                  className="chip"
                  style={{
                    cursor: "pointer",
                    fontSize: 11,
                    background: marked.has(q.id) ? "var(--warning-wash)" : "var(--surface-2)",
                    color: marked.has(q.id) ? "var(--warning-clr)" : "var(--text-dim)",
                  }}
                >
                  <Flag size={12} />
                  {marked.has(q.id) ? "Marked" : "Mark"}
                </button>
              </div>
            </div>

            <h2 className="title" style={{ fontSize: 24, lineHeight: 1.4, marginTop: 20, whiteSpace: "pre-line" }}>
              {q.prompt}
            </h2>

            <div className="stack-16" style={{ marginTop: 32 }}>
              <QuestionInput q={q} value={answers[q.id]} onChange={setAnswer} onToggleMultiple={toggleMultiple} />
            </div>

            <div className="between" style={{ marginTop: 40 }}>
              <button className="btn btn-ghost" onClick={() => go(index - 1)} disabled={index === 0}>
                <ChevronLeft size={16} /> Previous
              </button>
              <div className="lf-row" style={{ gap: 10 }}>
                <button className="btn btn-ghost btn-sm" onClick={() => go(index + 1)} disabled={index === total - 1}>
                  <SkipForward size={15} /> Skip
                </button>
                {index === total - 1 ? (
                  <button className="btn btn-solid" onClick={() => setReviewing(true)}>
                    Review <CheckCircle2 size={16} />
                  </button>
                ) : (
                  <button className="btn btn-quiet" onClick={() => go(index + 1)}>
                    Next <ChevronRight size={16} />
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : (
          <div className="surface pad-l fade-in">
            <h2 className="title">Review &amp; submit</h2>
            <div className="stack-16" style={{ marginTop: 20 }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }}>
                <Stat label="Answered" value={answeredCount} color="var(--success-clr)" />
                <Stat label="Not answered" value={total - answeredCount} color="var(--text-faint)" />
                <Stat label="Marked" value={marked.size} color="var(--warning-clr)" />
              </div>
              <p className="faint body-sm" style={{ lineHeight: 1.6 }}>
                You can still go back and change any answer. Once you submit, your responses are evaluated
                instantly and your mastery is recomputed.
              </p>
              <div className="lf-row" style={{ gap: 12 }}>
                <button className="btn btn-quiet" onClick={() => setReviewing(false)}>
                  Keep working
                </button>
                <button className="btn btn-solid" data-testid="quiz-submit" onClick={handleSubmit} disabled={submitting}>
                  {submitting ? <Loader2 size={16} className="animate-spin" /> : <CheckCircle2 size={16} />}
                  {submitLabel}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* palette rail */}
      <aside className="exam-rail-inner">
        <div className="lf-label" style={{ marginBottom: 16 }}>
          Questions
        </div>
        <div className="pal">
          {questions.map((qq, i) => {
            const answered = isAnswered(answers[qq.id]);
            const isMarked = marked.has(qq.id);
            const cls = [i === index && !reviewing ? "cur" : "", answered ? "done" : "", isMarked ? "marked" : ""]
              .filter(Boolean)
              .join(" ");
            return (
              <button key={qq.id} className={cls} onClick={() => go(i)} data-testid="quiz-number">
                {i + 1}
              </button>
            );
          })}
        </div>

        <div className="stack-8" style={{ marginTop: 24 }}>
          <div className="between">
            <span className="faint" style={{ fontSize: 13 }}>Answered</span>
            <span className="lf-mono" style={{ fontSize: 13 }}>
              {answeredCount}/{total}
            </span>
          </div>
          <Bar value={(answeredCount / total) * 100} />
        </div>

        <button
          className="btn btn-solid"
          data-testid="quiz-review"
          onClick={() => setReviewing(true)}
          style={{ width: "100%", marginTop: 24 }}
        >
          Review &amp; submit
        </button>

        <div className="surface" style={{ padding: "14px 16px", marginTop: 24 }}>
          <p className="faint body-sm" style={{ fontStyle: "italic", lineHeight: 1.5 }}>
            No distractions, no going back to the dashboard mid-exam. Full focus. This is how JEE feels.
          </p>
        </div>
      </aside>
    </div>
  );
}

function isAnswered(v: AnswerValue): boolean {
  if (v === null || v === undefined || v === "") return false;
  if (Array.isArray(v)) return v.length > 0;
  return true;
}

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="surface-2" style={{ padding: 14, textAlign: "center" }}>
      <div className="lf-mono" style={{ fontSize: 24, fontWeight: 700, color }}>
        {value}
      </div>
      <div className="faint" style={{ fontSize: 12, marginTop: 2 }}>
        {label}
      </div>
    </div>
  );
}

function QuestionInput({
  q,
  value,
  onChange,
  onToggleMultiple,
}: {
  q: Question;
  value: AnswerValue;
  onChange: (v: AnswerValue) => void;
  onToggleMultiple: (i: number) => void;
}) {
  if (q.type === "single_correct" && q.options) {
    return (
      <>
        {q.options.map((opt, i) => {
          const selected = value === i;
          return (
            <button
              key={opt.id}
              data-testid="quiz-option"
              onClick={() => onChange(i)}
              className={"opt" + (selected ? " sel" : "")}
            >
              <span className="ring" />
              <span className="lf-mono faint" style={{ fontSize: 14, flex: "none" }}>
                {String.fromCharCode(65 + i)}
              </span>
              <span className="body-lg" style={{ fontSize: 16 }}>
                {opt.text}
              </span>
            </button>
          );
        })}
      </>
    );
  }

  if (q.type === "multiple_correct" && q.options) {
    const arr = Array.isArray(value) ? (value as number[]) : [];
    return (
      <>
        <p className="faint body-sm">Select all that apply.</p>
        {q.options.map((opt, i) => {
          const selected = arr.includes(i);
          return (
            <button
              key={opt.id}
              data-testid="quiz-option"
              onClick={() => onToggleMultiple(i)}
              className={"opt" + (selected ? " sel" : "")}
            >
              <span
                className="ring"
                style={{ borderRadius: 6, ...(selected ? { background: "var(--indigo)", borderColor: "var(--indigo)" } : {}) }}
              />
              <span className="lf-mono faint" style={{ fontSize: 14, flex: "none" }}>
                {String.fromCharCode(65 + i)}
              </span>
              <span className="body-lg" style={{ fontSize: 16 }}>
                {opt.text}
              </span>
            </button>
          );
        })}
      </>
    );
  }

  // integer / numerical
  return (
    <div style={{ maxWidth: 320 }}>
      <p className="faint body-sm" style={{ marginBottom: 10 }}>
        Enter {q.type === "integer" ? "an integer" : "a numerical value"}
        {q.unit ? ` (in ${q.unit})` : ""}.
      </p>
      <input
        type="number"
        data-testid="quiz-number"
        inputMode={q.type === "integer" ? "numeric" : "decimal"}
        step={q.type === "integer" ? "1" : "any"}
        value={value === null || value === undefined ? "" : String(value)}
        onChange={(e) => onChange(e.target.value === "" ? null : e.target.value)}
        placeholder="Your answer"
        style={{
          width: "100%",
          background: "var(--surface-3)",
          border: 0,
          borderRadius: "var(--radius)",
          color: "var(--text)",
          padding: "12px 14px",
          fontSize: 16,
          fontFamily: "var(--font-mono)",
          outline: "none",
        }}
      />
    </div>
  );
}
