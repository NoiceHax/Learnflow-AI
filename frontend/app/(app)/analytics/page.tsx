"use client";

import { useEffect, useState } from "react";
import {
  Gauge,
  Clock,
  TrendingUp,
  CheckCircle2,
  Radar as RadarIcon,
  AlertTriangle,
  Trophy,
  Lightbulb,
} from "lucide-react";
import { ChapterRadar, MasteryBars } from "@/components/charts";
import { Card, CardContent } from "@/components/ui/card";
import { PageSkeleton } from "@/components/page-skeleton";
import { api } from "@/lib/api";
import { cn, masteryColor, masteryLabel } from "@/lib/utils";
import type { Dashboard } from "@/lib/types";

function sample<T>(arr: T[], n: number): T[] {
  if (arr.length <= n) return arr;
  const step = arr.length / n;
  return Array.from({ length: n }, (_, i) => arr[Math.floor(i * step)]);
}

export default function AnalyticsPage() {
  const [data, setData] = useState<Dashboard | null>(null);

  useEffect(() => {
    api.dashboard().then(setData);
  }, []);

  if (!data) {
    return <PageSkeleton variant="analytics" />;
  }

  const radarData = sample(
    data.chapter_mastery.map((c) => ({ chapter: c.chapter, mastery: c.mastery })),
    8
  );
  const subjectData = data.subject_mastery.map((s) => ({ label: s.subject, mastery: s.mastery }));
  const allChapters = data.chapter_mastery.map((c) => ({ label: c.chapter, mastery: c.mastery }));
  const interp = data.interpretations;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Analytics</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Numbers with meaning. Every metric comes with what to do next.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Mini icon={TrendingUp} label="Overall Progress" value={`${data.overall_progress}%`} />
        <Mini icon={Gauge} label="Accuracy" value={`${data.accuracy}%`} />
        <Mini icon={Clock} label="Time Spent" value={`${data.time_spent_hours} h`} />
        <Mini icon={CheckCircle2} label="Quizzes Attempted" value={`${data.quizzes_attempted}`} />
      </div>

      {/* Coach's read: interpretations under the metrics */}
      <Card>
        <CardContent className="space-y-3 p-6">
          <div className="flex items-center gap-2">
            <Lightbulb className="size-4 text-primary" />
            <h2 className="font-semibold">What your numbers mean</h2>
          </div>
          <Interp label="Accuracy" text={interp.accuracy} />
          <Interp label="Time spent" text={interp.time} />
          <Interp label="Focus" text={interp.weak} />
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <CardContent className="space-y-4 p-6">
            <div className="flex items-center gap-2">
              <RadarIcon className="size-4 text-primary" />
              <h2 className="font-semibold">Chapter Mastery</h2>
            </div>
            <ChapterRadar data={radarData} />
            <p className="rounded-md bg-secondary/50 p-3 text-sm text-muted-foreground">
              <span className="font-medium text-foreground">Read: </span>
              {interp.radar}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="space-y-4 p-6">
            <h2 className="font-semibold">Mastery by Subject</h2>
            <MasteryBars data={subjectData} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="space-y-4 p-6">
          <h2 className="font-semibold">All Chapters</h2>
          {allChapters.length === 0 ? (
            <p className="text-sm text-muted-foreground">Take the assessment to populate your chapter mastery.</p>
          ) : (
            <MasteryBars data={allChapters} />
          )}
        </CardContent>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <RankedList title="Weak Topics" icon={AlertTriangle} tone="warning" items={data.weak_topics} empty="No weak topics." />
        <RankedList title="Strong Topics" icon={Trophy} tone="success" items={data.strong_topics} empty="No mastered topics yet." />
      </div>
    </div>
  );
}

function Interp({ label, text }: { label: string; text: string }) {
  return (
    <div className="flex gap-3 rounded-lg border bg-secondary/30 p-3">
      <span className="shrink-0 text-sm font-semibold">{label}:</span>
      <span className="text-sm text-muted-foreground">{text}</span>
    </div>
  );
}

function Mini({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 p-5">
        <div className="flex size-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
          <Icon className="size-5" />
        </div>
        <div>
          <div className="text-xl font-bold tabular-nums">{value}</div>
          <div className="text-xs text-muted-foreground">{label}</div>
        </div>
      </CardContent>
    </Card>
  );
}

function RankedList({
  title,
  icon: Icon,
  tone,
  items,
  empty,
}: {
  title: string;
  icon: React.ElementType;
  tone: "warning" | "success";
  items: { chapter: string; subject: string; mastery: number }[];
  empty: string;
}) {
  return (
    <Card>
      <CardContent className="space-y-3 p-6">
        <div className="flex items-center gap-2">
          <Icon className={cn("size-4", tone === "warning" ? "text-amber-500" : "text-success")} />
          <h2 className="font-semibold">{title}</h2>
        </div>
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">{empty}</p>
        ) : (
          <ol className="space-y-3">
            {items.map((t, i) => (
              <li key={t.chapter} className="flex items-center gap-3">
                <span className="w-4 text-xs font-medium text-muted-foreground">{i + 1}</span>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-sm font-medium">{t.chapter}</div>
                  <div className="text-xs text-muted-foreground">{t.subject} · {masteryLabel(t.mastery)}</div>
                </div>
                <span className={cn("text-sm font-semibold tabular-nums", masteryColor(t.mastery))}>{t.mastery}%</span>
              </li>
            ))}
          </ol>
        )}
      </CardContent>
    </Card>
  );
}
