"use client";

import { CheckCircle2, XCircle, Target, Gauge, AlertTriangle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import type { AnswerValue, Question, QuizResult } from "@/lib/types";
import { cn } from "@/lib/utils";

function renderAnswer(q: Question | undefined, value: AnswerValue): string {
  if (value === null || value === undefined || value === "") return "Not answered";
  if (q?.options) {
    if (Array.isArray(value)) {
      return value.map((i) => String.fromCharCode(65 + Number(i))).join(", ");
    }
    const opt = q.options[Number(value)];
    return opt ? `${String.fromCharCode(65 + Number(value))}. ${opt.text}` : String(value);
  }
  return String(value);
}

export function QuizResultView({
  result,
  questions,
  mode = "final",
  onPrimary,
  primaryLabel,
  onSecondary,
  secondaryLabel,
  heading = "Results",
}: {
  result: QuizResult;
  questions: Question[];
  mode?: "practice" | "final";
  onPrimary: () => void;
  primaryLabel: string;
  onSecondary?: () => void;
  secondaryLabel?: string;
  heading?: string;
}) {
  const qById = new Map(questions.map((q) => [q.id, q]));
  const passed = result.score >= 80;
  const needsWork = result.score < 60;
  const isPractice = mode === "practice";
  const isFinal = mode === "final";

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="text-center">
        <p className="text-sm font-medium text-muted-foreground">{heading}</p>
        <div className={cn("mt-1 text-5xl font-bold tabular-nums", result.chapter_mastered || passed ? "text-success" : needsWork ? "text-destructive" : "text-primary")}>
          {result.score}%
        </div>
        <p className="mt-2 text-sm text-muted-foreground">
          {result.chapter_mastered
            ? "Chapter complete. You've mastered this section."
            : passed
              ? "Excellent. You're ready to move forward."
              : needsWork
                ? "Let's reinforce this with practice, then retake the final quiz."
                : isFinal
                  ? "Score 100% on the final quiz to complete this chapter."
                  : "Solid effort. Keep practicing your misses."}
        </p>
      </div>

      <div className="grid grid-cols-3 gap-3">
        <Metric icon={CheckCircle2} label="Correct" value={`${result.correct_count}/${result.total_questions}`} />
        <Metric icon={Gauge} label="Accuracy" value={`${result.accuracy}%`} />
        <Metric icon={Target} label="Score" value={`${result.score}%`} />
      </div>

      {result.chapter_mastered && (
        <Card className="border-success/40 bg-success/5">
          <CardContent className="p-4 text-sm">
            <p className="font-medium text-success">Chapter mastered</p>
            <p className="mt-1 text-muted-foreground">
              Perfect score on the final quiz. This chapter is complete and your path has been updated.
            </p>
          </CardContent>
        </Card>
      )}

      {result.adaptive && isFinal && !result.chapter_mastered && (result.adaptive.retired_count > 0 || result.adaptive.replacements_generated > 0) && (
        <Card>
          <CardContent className="space-y-2 p-4 text-sm">
            <p className="font-medium">Final quiz summary</p>
            {result.adaptive.retired_count > 0 && (
              <p className="text-muted-foreground">
                {result.adaptive.retired_count} missed question
                {result.adaptive.retired_count !== 1 ? "s were" : " was"} added to your practice set.
              </p>
            )}
            {result.adaptive.replacements_generated > 0 && (
              <p className="text-muted-foreground">
                {result.adaptive.replacements_generated} fresh question
                {result.adaptive.replacements_generated !== 1 ? "s" : ""} prepared for your next final attempt.
              </p>
            )}
            <p className="text-muted-foreground">
              Use Practice from the lesson to review misses, then retake the final quiz for 100%.
            </p>
          </CardContent>
        </Card>
      )}

      {isPractice && result.correct_count > 0 && (
        <Card>
          <CardContent className="p-4 text-sm text-muted-foreground">
            {result.correct_count} question{result.correct_count !== 1 ? "s" : ""} cleared from your practice set.
            {result.weak_concepts.length > 0 ? " Keep practicing the rest." : " Great work. Retake the final quiz when ready."}
          </CardContent>
        </Card>
      )}

      {result.weak_concepts.length > 0 && (
        <Card>
          <CardContent className="flex flex-wrap items-center gap-2 p-4">
            <AlertTriangle className="size-4 text-amber-500" />
            <span className="text-sm font-medium">Focus areas:</span>
            {result.weak_concepts.map((c) => (
              <Badge key={c} variant="warning">
                {c}
              </Badge>
            ))}
          </CardContent>
        </Card>
      )}

      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-muted-foreground">Question review</h3>
        {result.graded.map((g, i) => {
          const q = qById.get(g.question_id);
          return (
            <Card key={g.question_id}>
              <CardContent className="space-y-3 p-4">
                <div className="flex items-start gap-3">
                  {g.correct ? (
                    <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" />
                  ) : (
                    <XCircle className="mt-0.5 size-5 shrink-0 text-destructive" />
                  )}
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs font-medium text-muted-foreground">Q{i + 1}</span>
                      <Badge variant="outline">{g.concept}</Badge>
                    </div>
                    {q && <p className="whitespace-pre-line text-sm">{q.prompt}</p>}
                  </div>
                </div>
                <Separator />
                <div className="grid gap-1 pl-8 text-sm sm:grid-cols-2">
                  <div>
                    <span className="text-muted-foreground">Your answer: </span>
                    <span className={g.correct ? "text-success" : "text-destructive"}>{renderAnswer(q, g.your_answer)}</span>
                  </div>
                  {!g.correct && (
                    <div>
                      <span className="text-muted-foreground">Correct answer: </span>
                      <span className="text-success">{renderAnswer(q, g.correct_answer)}</span>
                    </div>
                  )}
                </div>
                {g.solution && (
                  <p className="rounded-lg bg-secondary/60 p-3 pl-3 text-sm text-muted-foreground sm:ml-8">
                    <span className="font-medium text-foreground">Solution. </span>
                    {g.solution}
                  </p>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      <div className="flex flex-wrap justify-center gap-3 pt-2">
        {onSecondary && secondaryLabel && (
          <Button variant="outline" onClick={onSecondary}>
            {secondaryLabel}
          </Button>
        )}
        <Button onClick={onPrimary}>{primaryLabel}</Button>
      </div>
    </div>
  );
}

function Metric({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center gap-1 p-4 text-center">
        <Icon className="size-5 text-primary" />
        <div className="text-lg font-bold tabular-nums">{value}</div>
        <div className="text-xs text-muted-foreground">{label}</div>
      </CardContent>
    </Card>
  );
}
