"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useRef, useState } from "react";
import { QuizSkeleton } from "@/components/page-skeleton";
import { QuizEngine } from "@/components/quiz-engine";
import { QuizResultView } from "@/components/quiz-result";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import { MIN_QUIZ_QUESTIONS, type AnswerValue, type Question, type QuizResult } from "@/lib/types";

type QuizMode = "practice" | "final" | "pyq";

function ExamQuizContent() {
  const params = useParams<{ chapterId: string }>();
  const searchParams = useSearchParams();
  const chapterId = params.chapterId;
  const router = useRouter();
  const rawMode = searchParams.get("mode");
  const mode: QuizMode = rawMode === "pyq" ? "pyq" : rawMode === "practice" ? "practice" : "final";
  const isPractice = mode === "practice";

  const [stage, setStage] = useState<"loading" | "quiz" | "submitting" | "result" | "error">("loading");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [rateLimited, setRateLimited] = useState(false);
  const [retryCooldown, setRetryCooldown] = useState(0);
  const retryTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const pyqYear = searchParams.get("pyq_year") ? parseInt(searchParams.get("pyq_year")!) : undefined;
  const pyqExam = searchParams.get("pyq_exam") || undefined;

  const load = useCallback(async () => {
    setStage("loading");
    setResult(null);
    setError(null);
    try {
      let qs: Question[];
      if (mode === "pyq") {
        qs = await api.quizQuestions(chapterId, 10, "practice", {
          is_pyq: true,
          pyq_year: pyqYear,
          pyq_exam: pyqExam,
        });
      } else {
        qs = await api.quizQuestions(chapterId, isPractice ? 5 : 6, mode);
      }
      
      const minQs = mode === "pyq" ? 1 : MIN_QUIZ_QUESTIONS;
      if (qs.length < minQs) {
        setError(
          mode === "pyq"
            ? "No matching Previous Year Questions (PYQs) found for this chapter with the selected filters."
            : isPractice
            ? "Not enough practice questions yet. Run pregenerate-backups on the server, then try again."
            : "Not enough questions for a quiz in this chapter yet.",
        );
        setStage("error");
        return;
      }
      setQuestions(qs);
      setStage("quiz");
    } catch (e) {
      if (e instanceof ApiError && e.status === 429) {
        setRateLimited(true);
        setRetryCooldown(30);
        setError(e.message || "Too many quiz requests. Please wait a moment.");
        // Start cooldown countdown
        if (retryTimerRef.current) clearInterval(retryTimerRef.current);
        let remaining = 30;
        retryTimerRef.current = setInterval(() => {
          remaining -= 1;
          setRetryCooldown(remaining);
          if (remaining <= 0) {
            if (retryTimerRef.current) clearInterval(retryTimerRef.current);
            retryTimerRef.current = null;
            setRateLimited(false);
          }
        }, 1000);
      } else {
        setError(e instanceof ApiError ? e.message : "Could not load this quiz.");
      }
      setStage("error");
    }
  }, [chapterId, mode, isPractice, pyqYear, pyqExam]);

  useEffect(() => {
    load();
  }, [load]);

  async function submit(answers: { question_id: string; answer: AnswerValue }[], timeTaken: number) {
    setStage("submitting");
    try {
      const res = await api.submitQuiz(chapterId, answers, timeTaken, mode === "pyq" ? "practice" : mode);
      setResult(res);
      setStage("result");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not submit your quiz.");
      setStage("quiz");
    }
  }

  const chapterLabel = questions[0]?.chapter ?? "";
  const title = mode === "pyq"
    ? `PYQ Quiz · ${chapterLabel}`
    : isPractice
    ? `Practice Quiz · ${chapterLabel}`
    : `Final Quiz · ${chapterLabel}`;
  const subtitle = mode === "pyq"
    ? `Practicing past year JEE questions from ${pyqExam || "JEE"} ${pyqYear ? `(${pyqYear})` : ""}`
    : isPractice
    ? "Mostly fresh AI questions each round. Get one right and it leaves your set; a new one replaces it."
    : "Score 100% to complete this chapter and unlock the next.";

  const quizKey = questions.map((q) => q.id).join(",");

  if (stage === "loading") {
    return <QuizSkeleton />;
  }

  if (stage === "error") {
    return (
      <Card className="mx-auto max-w-md">
        <CardContent className="space-y-4 p-6 text-center">
          {rateLimited ? (
            <>
              <div className="flex items-center justify-center gap-2 text-amber-500">
                <span className="text-xl">⏳</span>
                <p className="text-sm font-medium">Rate Limited</p>
              </div>
              <p className="text-xs text-muted-foreground">{error}</p>
              <div className="mx-auto w-48 overflow-hidden rounded-full bg-muted" style={{ height: 4 }}>
                <div
                  className="h-full rounded-full bg-amber-500 transition-all duration-1000 ease-linear"
                  style={{ width: `${Math.max(0, (retryCooldown / 30) * 100)}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">
                {retryCooldown > 0 ? `Ready in ${retryCooldown}s…` : "Ready! Try again."}
              </p>
              <Button onClick={load} disabled={retryCooldown > 0}>Try again</Button>
            </>
          ) : (
            <>
              <p className="text-sm text-destructive">{error}</p>
              <div className="flex justify-center gap-2">
                {isPractice ? (
                  <Button variant="outline" onClick={() => router.push(`/exam/quiz/${chapterId}?mode=final`)}>
                    Take final quiz
                  </Button>
                ) : (
                  <Button variant="outline" onClick={() => router.push("/dashboard")}>
                    Dashboard
                  </Button>
                )}
                <Button onClick={load}>Try again</Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    );
  }

  if (stage === "result" && result) {
    return (
      <QuizResultView
        result={result}
        questions={questions}
        mode={mode === "pyq" ? "practice" : mode}
        heading={title}
        primaryLabel={result.chapter_mastered ? "Back to dashboard" : isPractice ? "Back to lesson" : "Back to dashboard"}
        onPrimary={() =>
          router.push(result.chapter_mastered || !isPractice ? "/dashboard" : `/lessons/${chapterId}`)
        }
        secondaryLabel={isPractice ? "Practice again" : "Retake final quiz"}
        onSecondary={load}
      />
    );
  }

  return (
    <QuizEngine
      key={quizKey}
      questions={questions}
      title={title}
      subtitle={subtitle}
      submitLabel={isPractice ? "Submit practice" : "Submit final quiz"}
      submitting={stage === "submitting"}
      onSubmit={submit}
    />
  );
}

export default function ExamQuizPage() {
  return (
    <Suspense fallback={<QuizSkeleton />}>
      <ExamQuizContent />
    </Suspense>
  );
}
