"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AlertTriangle, ArrowRight, BookOpen, Clock, TrendingUp } from "lucide-react";
import { MasteryJourneyMap } from "@/components/mastery-journey";
import { PageSkeleton } from "@/components/page-skeleton";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { fmtDate } from "@/lib/utils";
import type { Dashboard } from "@/lib/types";

function SectionLabel({ children, action }: { children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <div className="between" style={{ marginBottom: 18 }}>
      <div className="lf-label">{children}</div>
      {action}
    </div>
  );
}

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

function DashSkeleton() {
  return <PageSkeleton variant="dashboard" />;
}

function MetricCard({
  label,
  value,
  sub,
  icon: Icon,
}: {
  label: string;
  value: string;
  sub?: string;
  icon: React.ElementType;
}) {
  return (
    <div className="surface pad" style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
      <div
        style={{
          width: 40,
          height: 40,
          borderRadius: 10,
          background: "var(--indigo-wash)",
          color: "var(--indigo-bright)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          flex: "none",
        }}
      >
        <Icon size={18} />
      </div>
      <div>
        <div className="lf-mono geist" style={{ fontSize: 28, fontWeight: 700, letterSpacing: "-0.03em" }}>
          {value}
        </div>
        <div className="geist" style={{ fontWeight: 500, fontSize: 14, marginTop: 2 }}>
          {label}
        </div>
        {sub && (
          <div className="faint body-sm" style={{ marginTop: 4 }}>
            {sub}
          </div>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState<Dashboard | null>(null);

  useEffect(() => {
    api.dashboard().then(setData);
  }, []);

  if (!data) return <DashSkeleton />;

  const firstName = user?.name.split(" ")[0] ?? "there";
  const journey = data.mastery_journey;
  const topRec = data.ai_recommendations[0];
  const dateLabel = new Date().toLocaleDateString(undefined, { weekday: "long", day: "numeric", month: "long" });

  return (
    <div style={{ paddingBottom: 48 }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div className="lf-label" style={{ marginBottom: 12 }}>
          {dateLabel}
        </div>
        <h1 className="headline fade-in">
          {greeting()}, {firstName}.
        </h1>
        <p className="body-lg dim fade-in" style={{ marginTop: 8, maxWidth: 640 }}>
          Your adaptive path updates after every quiz. Weak concepts resurface until mastered.
        </p>
      </div>

      {/* Top metrics */}
      <div className="dash-metrics lf-section" style={{ marginBottom: 40 }}>
        <MetricCard
          icon={TrendingUp}
          label="Overall Mastery"
          value={`${Math.round(data.overall_progress)}%`}
          sub={`${data.chapters_completed} chapters mastered`}
        />
        <MetricCard
          icon={BookOpen}
          label="Current Subject"
          value={journey.current_subject ?? "-"}
          sub={journey.current_module ? `Module: ${journey.current_module}` : "Complete assessment to begin"}
        />
        <MetricCard
          icon={Clock}
          label="Accuracy"
          value={`${data.accuracy}%`}
          sub={`${data.time_spent_hours}h invested`}
        />
      </div>

      {/* Mastery Journey centerpiece */}
      <section className="lf-section" style={{ marginBottom: 48 }}>
        <SectionLabel
          action={
            <span className="faint lf-mono" style={{ fontSize: 11 }}>
              {journey.stats.mastered ?? 0} mastered · {journey.stats.revision ?? 0} revision ·{" "}
              {journey.stats.locked ?? 0} locked
            </span>
          }
        >
          Mastery Journey
        </SectionLabel>
        <MasteryJourneyMap journey={journey} />
      </section>

      {/* Bottom row */}
      <div className="dash-bottom">
        <div>
          <SectionLabel>Weak Concepts</SectionLabel>
          {data.weak_areas.length === 0 ? (
            <p className="faint body-sm">No weak areas. Excellent work.</p>
          ) : (
            <div className="fade-in">
              {data.weak_areas.slice(0, 5).map((w) => (
                <Link key={w.chapter_id} href={`/lessons/${w.chapter_id}`} className="lrow">
                  <div className="lf-row" style={{ gap: 12, minWidth: 0 }}>
                    <AlertTriangle size={16} style={{ color: "var(--warning-clr)", flex: "none" }} />
                    <div style={{ minWidth: 0 }}>
                      <div className="geist" style={{ fontWeight: 500, fontSize: 14 }}>
                        {w.chapter}
                      </div>
                      <div className="faint" style={{ fontSize: 12 }}>
                        {w.mastery}% · {w.subject}
                      </div>
                    </div>
                  </div>
                  <span className="lf-mono" style={{ fontSize: 12, color: "var(--warning-clr)" }}>
                    {w.mastery}%
                  </span>
                </Link>
              ))}
            </div>
          )}
        </div>

        <div>
          <SectionLabel>Recommended Next Step</SectionLabel>
          {topRec ? (
            <div className="surface pad fade-in">
              <div className="lf-label" style={{ color: "var(--indigo-bright)", marginBottom: 8 }}>
                {topRec.kind}
              </div>
              <div className="geist" style={{ fontWeight: 600, fontSize: 16 }}>
                {topRec.title}
              </div>
              <p className="faint body-sm" style={{ marginTop: 8, lineHeight: 1.55 }}>
                {topRec.text}
              </p>
              {topRec.action_chapter_id && (
                <Link
                  href={`/lessons/${topRec.action_chapter_id}`}
                  className="btn btn-solid btn-sm"
                  style={{ marginTop: 16 }}
                >
                  {topRec.action_label} <ArrowRight size={14} />
                </Link>
              )}
            </div>
          ) : (
            <p className="faint body-sm">Take a quiz to unlock tailored recommendations.</p>
          )}
        </div>

        <div>
          <SectionLabel>Weekly Activity</SectionLabel>
          {data.recent_activity.length === 0 ? (
            <p className="faint body-sm">No activity yet.</p>
          ) : (
            <div className="fade-in">
              {data.recent_activity.slice(0, 6).map((a, i) => (
                <div key={i} className="lrow" style={{ cursor: "default" }}>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: 14 }}>{a.title}</div>
                    <div className="faint" style={{ fontSize: 12 }}>
                      {fmtDate(a.timestamp)}
                    </div>
                  </div>
                  {a.score != null && (
                    <span
                      className="lf-mono"
                      style={{
                        fontSize: 12,
                        color:
                          a.score >= 80 ? "var(--success-clr)" : a.score < 50 ? "var(--error-clr)" : "var(--text-faint)",
                      }}
                    >
                      {a.score}%
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
