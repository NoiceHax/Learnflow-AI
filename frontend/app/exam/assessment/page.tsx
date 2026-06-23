"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ClipboardCheck, Sparkles } from "lucide-react";
import { KnowledgeProfile } from "@/components/knowledge-profile";
import { QuizEngine } from "@/components/quiz-engine";
import { QuizSkeleton } from "@/components/page-skeleton";
import { enterFullscreen } from "@/components/exam-shell";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { AnswerValue, AssessmentResult, Question } from "@/lib/types";

type Stage = "intro" | "loading" | "quiz" | "submitting" | "result";

export default function ExamAssessmentPage() {
  const router = useRouter();
  const { user, refresh } = useAuth();
  const [stage, setStage] = useState<Stage>("intro");
  const [questions, setQuestions] = useState<Question[]>([]);
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Already onboarded — skip assessment, unless we're showing the post-submit profile.
    if (user?.onboarded && stage !== "result" && stage !== "submitting") {
      router.replace("/dashboard");
    }
  }, [user, router, stage]);

  async function start() {
    setStage("loading");
    setError(null);
    setResult(null);
    await enterFullscreen();
    try {
      const qs = await api.assessmentQuestions();
      setQuestions(qs);
      setStage("quiz");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not load the assessment.");
      setStage("intro");
    }
  }

  async function submit(answers: { question_id: string; answer: AnswerValue }[], timeTaken: number) {
    setStage("submitting");
    try {
      const res = await api.submitAssessment(answers, timeTaken);
      setResult(res);
      setStage("result");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not submit the assessment.");
      setStage("quiz");
    }
  }

  if (stage === "loading" || stage === "submitting") {
    return <QuizSkeleton />;
  }

  if (stage === "intro") {
    return (
      <div className="mx-auto max-w-2xl">
        <Card>
          <CardContent className="space-y-5 p-8">
            <div className="flex size-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <ClipboardCheck className="size-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Initial Assessment</h1>
              <p className="mt-2 text-muted-foreground">
                A focused diagnostic across Organic Chemistry, Inorganic Chemistry, Physics and
                Mathematics. You&apos;re entering a distraction-free exam environment. Sidebars and
                navigation are hidden so you can concentrate.
              </p>
            </div>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>• Mixed question types: single &amp; multiple correct, integer and numerical.</li>
              <li>• Timer, question palette and mark-for-review, just like the real exam.</li>
              <li>• One-time diagnostic. Your knowledge profile shapes everything that follows.</li>
            </ul>
            {error && <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>}
            <Button size="lg" onClick={start}>
              <Sparkles className="size-4" />
              Begin assessment
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (stage === "quiz") {
    return (
      <QuizEngine
        questions={questions}
        title="Initial Assessment"
        subtitle="Across all four subjects"
        submitLabel="Submit assessment"
        onSubmit={submit}
      />
    );
  }

  return (
    <KnowledgeProfile
      result={result!}
      onContinue={async () => {
        await refresh();
        router.push("/dashboard");
      }}
    />
  );
}
