"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  ArrowLeft,
  PencilLine,
  MessageCircleQuestion,
  Lightbulb,
  Sigma,
  ListChecks,
  AlertTriangle,
  Star,
  Dumbbell,
} from "lucide-react";
import { PageSkeleton } from "@/components/page-skeleton";
import { useSocrates } from "@/components/socrates-context";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { api, ApiError } from "@/lib/api";
import type { Lesson } from "@/lib/types";

export default function LessonPage() {
  const params = useParams<{ chapterId: string }>();
  const router = useRouter();
  const { setContext, clearContext, setOpen } = useSocrates();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .lesson(params.chapterId)
      .then(setLesson)
      .catch((e) => setError(e instanceof ApiError ? e.message : "Could not load this lesson."));
  }, [params.chapterId]);

  // Feed the current lesson to Socrates so the floating tutor already knows the
  // subject, chapter, formulas and examples on screen.
  useEffect(() => {
    if (!lesson) return;
    setContext({
      chapter: lesson.chapter,
      formulas: lesson.content.formulas.map((f) => `${f.name}: ${f.expr}`),
      examples: lesson.content.examples.map((e) => e.problem),
    });
    return () => clearContext();
  }, [lesson, setContext, clearContext]);

  if (error) {
    return (
      <Card className="mx-auto max-w-md">
        <CardContent className="space-y-4 p-6 text-center">
          <p className="text-sm text-destructive">{error}</p>
          <Button onClick={() => router.push("/lessons")}>Back to lessons</Button>
        </CardContent>
      </Card>
    );
  }

  if (!lesson) {
    return <PageSkeleton variant="lesson" />;
  }

  const c = lesson.content;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="space-y-3">
        <Button variant="ghost" size="sm" className="-ml-2 w-fit" asChild>
          <Link href="/lessons">
            <ArrowLeft className="size-4" /> Lessons
          </Link>
        </Button>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{lesson.chapter}</h1>
            <Badge variant="secondary" className="mt-2">
              {lesson.generated_by_ai ? "AI-generated" : "Premium coaching material"}
            </Badge>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={() => setOpen(true)}>
              <MessageCircleQuestion className="size-4" /> Ask Socrates
            </Button>
            <Button asChild>
              <Link href={`/exam/quiz/${lesson.chapter_id}?mode=final`}>
                <PencilLine className="size-4" /> Final quiz
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/exam/quiz/${lesson.chapter_id}?mode=practice`}>
                <PencilLine className="size-4" /> Practice
              </Link>
            </Button>
          </div>
        </div>
      </div>

      <Section icon={Lightbulb} title="Theory">
        <p className="whitespace-pre-line leading-relaxed text-muted-foreground">{c.theory}</p>
      </Section>

      <Section icon={ListChecks} title="Key Concepts">
        <ul className="space-y-2">
          {c.key_concepts.map((k, i) => (
            <li key={i} className="flex gap-2 text-sm">
              <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" />
              <span>{k}</span>
            </li>
          ))}
        </ul>
      </Section>

      <Section icon={Sigma} title="Formula Sheet">
        <div className="grid gap-2 sm:grid-cols-2">
          {c.formulas.map((f, i) => (
            <div key={i} className="rounded-lg border bg-secondary/40 p-3">
              <div className="text-xs font-medium text-muted-foreground">{f.name}</div>
              <div className="mt-1 font-mono text-sm">{f.expr}</div>
            </div>
          ))}
        </div>
      </Section>

      <Section icon={Star} title="Solved Examples">
        <div className="space-y-3">
          {c.examples.map((ex, i) => (
            <div key={i} className="rounded-lg border p-4">
              <div className="text-sm font-medium">
                <span className="text-primary">Q{i + 1}. </span>
                {ex.problem}
              </div>
              <div className="mt-2 rounded-md bg-secondary/50 p-3 text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Solution. </span>
                {ex.solution}
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section icon={AlertTriangle} title="Common Mistakes">
        <ul className="space-y-2">
          {c.common_mistakes.map((m, i) => (
            <li key={i} className="flex gap-2 text-sm">
              <AlertTriangle className="mt-0.5 size-4 shrink-0 text-amber-500" />
              <span>{m}</span>
            </li>
          ))}
        </ul>
      </Section>

      <Section icon={Star} title="PYQ Highlights">
        <ul className="space-y-2">
          {c.pyq_highlights.map((p, i) => (
            <li key={i} className="flex gap-2 text-sm">
              <span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-primary" />
              <span>{p}</span>
            </li>
          ))}
        </ul>
      </Section>

      <Section icon={Dumbbell} title="Practice Problems">
        <div className="grid gap-3 sm:grid-cols-3">
          {(["easy", "medium", "advanced"] as const).map((lvl) => (
            <div key={lvl} className="rounded-lg border p-4">
              <Badge
                variant={lvl === "easy" ? "success" : lvl === "advanced" ? "destructive" : "warning"}
                className="mb-2 capitalize"
              >
                {lvl}
              </Badge>
              <p className="text-sm text-muted-foreground">{c.practice[lvl]}</p>
            </div>
          ))}
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button asChild>
            <Link href={`/exam/quiz/${lesson.chapter_id}?mode=final`}>
              <PencilLine className="size-4" /> Final quiz
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href={`/exam/quiz/${lesson.chapter_id}?mode=practice`}>
              <PencilLine className="size-4" /> Practice
            </Link>
          </Button>
        </div>
      </Section>
    </div>
  );
}

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: React.ElementType;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <Card>
      <CardContent className="space-y-3 p-6">
        <div className="flex items-center gap-2">
          <Icon className="size-5 text-primary" />
          <h2 className="text-lg font-semibold">{title}</h2>
        </div>
        {children}
      </CardContent>
    </Card>
  );
}
