"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { ClipboardCheck, ArrowRight, Sparkles } from "lucide-react";
import { MasteryBars } from "@/components/charts";
import { QuizEngine } from "@/components/quiz-engine";
import { QuizSkeleton } from "@/components/page-skeleton";
import { enterFullscreen } from "@/components/exam-shell";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
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
    if (user?.onboarded) {
      router.replace("/dashboard");
    }
  }, [user, router]);

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
      await refresh();
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

  return <KnowledgeProfile result={result!} onContinue={() => router.push("/dashboard")} />;
}

function KnowledgeProfile({ result, onContinue }: { result: AssessmentResult; onContinue: () => void }) {
  const subjectData = Object.entries(result.subject_scores).map(([slug, mastery]) => ({
    label: slugLabel(slug),
    mastery,
  }));
  const sortedMap = [...result.knowledge_map].sort((a, b) => a.score - b.score);

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="text-center">
        <Badge variant="default" className="mb-2">
          Knowledge Profile
        </Badge>
        <h1 className="text-3xl font-bold tracking-tight">
          You scored <span className="text-primary">{result.score}%</span>
        </h1>
        <p className="mt-2 text-muted-foreground">
          {result.correct_count} of {result.total_questions} correct. Your personalised plan is ready on
          the dashboard.
        </p>
      </div>

      <Card>
        <CardContent className="space-y-4 p-6">
          <h2 className="font-semibold">Mastery by subject</h2>
          <MasteryBars data={subjectData} />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="space-y-4 p-6">
          <h2 className="font-semibold">Chapter knowledge map</h2>
          <div className="flex flex-wrap gap-2">
            {sortedMap.map((c) => (
              <span
                key={c.slug}
                className={cn(
                  "rounded-full border px-3 py-1 text-xs font-medium",
                  c.score >= 80
                    ? "border-success/40 bg-success/10 text-success"
                    : c.score >= 60
                      ? "border-primary/40 bg-primary/10 text-primary"
                      : c.score >= 40
                        ? "border-amber-500/40 bg-amber-500/10 text-amber-600 dark:text-amber-400"
                        : "border-destructive/40 bg-destructive/10 text-destructive"
                )}
              >
                {c.chapter} · {c.score}%
              </span>
            ))}
          </div>
          <p className="text-xs text-muted-foreground">
            Weak chapters are prioritised on your dashboard with extra practice; the system decides what
            to teach next.
          </p>
        </CardContent>
      </Card>

      <div className="flex justify-center">
        <Button size="lg" onClick={onContinue}>
          Go to my dashboard <ArrowRight className="size-4" />
        </Button>
      </div>
    </div>
  );
}

function slugLabel(slug: string): string {
  return slug
    .split("-")
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}
