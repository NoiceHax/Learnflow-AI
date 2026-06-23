"use client";

import { useParams, useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useState } from "react";
import { QuizSkeleton } from "@/components/page-skeleton";
import { QuizEngine } from "@/components/quiz-engine";
import { QuizResultView } from "@/components/quiz-result";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import { MIN_QUIZ_QUESTIONS, type AnswerValue, type Question, type QuizResult } from "@/lib/types";

type QuizMode = "practice" | "final";

function ExamQuizContent() {
  const params = useParams<{ chapterId: string }>();
  const searchParams = useSearchParams();
  const chapterId = params.chapterId;
  const router = useRouter();
  const rawMode = searchParams.get("mode");
  const mode: QuizMode = rawMode === "practice" ? "practice" : "final";
  const isPractice = mode === "practice";

  const [stage, setStage] = useState<"loading" | "quiz" | "submitting" | "result" | "error">("loading");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [result, setResult] = useState<QuizResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setStage("loading");
    setResult(null);
    setError(null);
    try {
      const qs = await api.quizQuestions(chapterId, isPractice ? 5 : 6, mode);
      if (qs.length < MIN_QUIZ_QUESTIONS) {
        setError(
          isPractice
            ? "Not enough practice questions yet. Run pregenerate-backups on the server, then try again."
            : "Not enough questions for a quiz in this chapter yet.",
        );
        setStage("error");
        return;
      }
      setQuestions(qs);
      setStage("quiz");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not load this quiz.");
      setStage("error");
    }
  }, [chapterId, mode, isPractice]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setStage("loading");
      setResult(null);
      setError(null);
      try {
        const qs = await api.quizQuestions(chapterId, isPractice ? 5 : 6, mode);
        if (cancelled) return;
        if (qs.length < MIN_QUIZ_QUESTIONS) {
          setError(
            isPractice
              ? "Not enough practice questions yet. Run pregenerate-backups on the server, then try again."
              : "Not enough questions for a quiz in this chapter yet.",
          );
          setStage("error");
          return;
        }
        setQuestions(qs);
        setStage("quiz");
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof ApiError ? e.message : "Could not load this quiz.");
          setStage("error");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [chapterId, mode, isPractice]);

  async function submit(answers: { question_id: string; answer: AnswerValue }[], timeTaken: number) {
    setStage("submitting");
    try {
      const res = await api.submitQuiz(chapterId, answers, timeTaken, mode);
      setResult(res);
      setStage("result");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not submit your quiz.");
      setStage("quiz");
    }
  }

  const chapterLabel = questions[0]?.chapter ?? "";
  const title = isPractice ? `Practice Quiz · ${chapterLabel}` : `Final Quiz · ${chapterLabel}`;
  const subtitle = isPractice
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
        </CardContent>
      </Card>
    );
  }

  if (stage === "result" && result) {
    return (
      <QuizResultView
        result={result}
        questions={questions}
        mode={mode}
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
