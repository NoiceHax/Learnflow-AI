"use client";

import { ArrowRight } from "lucide-react";
import { MasteryBars } from "@/components/charts";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import type { AssessmentResult } from "@/lib/types";

function slugLabel(slug: string): string {
  return slug
    .split("-")
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(" ");
}

export function KnowledgeProfile({
  result,
  onContinue,
  continueLabel = "Go to my dashboard",
}: {
  result: AssessmentResult;
  onContinue?: () => void | Promise<void>;
  continueLabel?: string;
}) {
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
          {result.correct_count} of {result.total_questions} correct.
          {onContinue
            ? " Your personalised plan is ready on the dashboard."
            : " Saved from your initial assessment."}
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
        </CardContent>
      </Card>

      {onContinue && (
        <div className="flex justify-center">
          <Button size="lg" onClick={onContinue}>
            {continueLabel} <ArrowRight className="size-4" />
          </Button>
        </div>
      )}
    </div>
  );
}
