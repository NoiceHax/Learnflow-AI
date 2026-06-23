"use client";

import { useEffect, useState } from "react";
import { KnowledgeProfile } from "@/components/knowledge-profile";
import { QuizResultView } from "@/components/quiz-result";
import { QuizSkeleton } from "@/components/page-skeleton";
import { api, ApiError } from "@/lib/api";
import type { ExamHistoryItem, ExamReport } from "@/lib/types";

export function ExamHistoryReportModal({
  item,
  onClose,
}: {
  item: ExamHistoryItem | null;
  onClose: () => void;
}) {
  const [report, setReport] = useState<ExamReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!item) {
      setReport(null);
      setError(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    api
      .examReport(item.kind, item.id)
      .then((data) => {
        if (!cancelled) setReport(data);
      })
      .catch((e) => {
        if (!cancelled) {
          setError(e instanceof ApiError ? e.message : "Could not load this report.");
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [item]);

  useEffect(() => {
    if (!item) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = "";
    };
  }, [item, onClose]);

  if (!item) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-background/80 p-4 backdrop-blur-sm sm:p-8"
      role="dialog"
      aria-modal="true"
      aria-label={`Report: ${item.title}`}
      onClick={onClose}
    >
      <div
        className="relative my-4 w-full max-w-4xl rounded-xl border bg-background shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="sticky top-0 z-10 border-b bg-background/95 px-4 py-3 backdrop-blur sm:px-6">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Exam report</p>
          <h2 className="text-lg font-semibold">{item.title}</h2>
        </div>

        <div className="p-4 sm:p-6">
          {loading && <QuizSkeleton />}
          {error && (
            <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>
          )}
          {!loading && !error && report?.kind === "assessment" && report.assessment && (
            <KnowledgeProfile result={report.assessment} />
          )}
          {!loading && !error && report?.kind === "final_quiz" && report.quiz_result && (
            <>
              {!report.detail_available && (
                <p className="mb-4 rounded-md bg-secondary/60 px-3 py-2 text-sm text-muted-foreground">
                  Score summary only — question-by-question review was not saved for this attempt.
                </p>
              )}
              <QuizResultView
                result={report.quiz_result}
                questions={report.questions ?? []}
                mode="final"
                heading={item.title}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
