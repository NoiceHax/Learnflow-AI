"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { BookOpen, PencilLine, Star } from "lucide-react";
import { SubjectIcon } from "@/components/subject-icon";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PageSkeleton } from "@/components/page-skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import type { Subject } from "@/lib/types";

export default function LessonsPage() {
  const [subjects, setSubjects] = useState<Subject[] | null>(null);

  useEffect(() => {
    api.subjects().then(setSubjects);
  }, []);

  if (!subjects) {
    return <PageSkeleton variant="lessons" />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Lessons</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Pilot syllabus: 3 chapters per subject. Locked topics open in a later release.
        </p>
      </div>

      <Tabs defaultValue={subjects[0]?.slug}>
        <TabsList className="flex h-auto flex-wrap justify-start gap-1">
          {subjects.map((s) => (
            <TabsTrigger key={s.slug} value={s.slug} className="gap-2">
              <SubjectIcon icon={s.icon} />
              {s.name}
            </TabsTrigger>
          ))}
        </TabsList>

        {subjects.map((s) => (
          <TabsContent key={s.slug} value={s.slug}>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {s.chapters.map((c) => {
                const locked = c.unlocked === false;
                return (
                <Card
                  key={c.id}
                  className={locked ? "flex flex-col opacity-60" : "card-interactive flex flex-col"}
                >
                  <CardContent className="flex flex-1 flex-col gap-3 p-5">
                    <div className="flex items-start justify-between">
                      <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <SubjectIcon icon={s.icon} />
                      </div>
                      <div className="flex flex-col items-end gap-1">
                        {locked && (
                          <Badge variant="secondary" className="text-[10px]">
                            Locked
                          </Badge>
                        )}
                        <Badge variant="secondary" className="gap-1">
                          <Star className="size-3" /> Weight {c.jee_weightage}
                        </Badge>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold">{c.chapter_name}</div>
                      <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{c.description}</p>
                    </div>
                    <div className="flex flex-col gap-2">
                      {locked ? (
                        <>
                          <Button variant="outline" size="sm" className="w-full" disabled>
                            <BookOpen className="size-4" /> Lesson
                          </Button>
                          <div className="flex gap-2">
                            <Button size="sm" className="flex-1" disabled>
                              <PencilLine className="size-4" /> Final
                            </Button>
                            <Button variant="outline" size="sm" className="flex-1" disabled>
                              <PencilLine className="size-4" /> Practice
                            </Button>
                          </div>
                        </>
                      ) : (
                        <>
                          <Button variant="outline" size="sm" className="w-full" asChild>
                            <Link href={`/lessons/${c.id}`}>
                              <BookOpen className="size-4" /> Lesson
                            </Link>
                          </Button>
                          <div className="flex gap-2">
                            <Button size="sm" className="flex-1" asChild>
                              <Link href={`/exam/quiz/${c.id}?mode=final`}>
                                <PencilLine className="size-4" /> Final
                              </Link>
                            </Button>
                            <Button variant="outline" size="sm" className="flex-1" asChild>
                              <Link href={`/exam/quiz/${c.id}?mode=practice`}>
                                <PencilLine className="size-4" /> Practice
                              </Link>
                            </Button>
                          </div>
                        </>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );})}
            </div>
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
