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

      {/* JEE Score Predictor Section */}
      <section className="lf-section" style={{ marginBottom: 48 }}>
        <SectionLabel>JEE Mains Score Predictor</SectionLabel>
        <div
          className="surface pad fade-in"
          style={{
            background:
              "linear-gradient(135deg, var(--surface-2) 0%, color-mix(in srgb, var(--indigo) 6%, var(--surface-2)) 100%)",
            border: "1px solid color-mix(in srgb, var(--indigo) 22%, transparent)",
            borderRadius: 16,
          }}
        >
          {/* Header row */}
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <span
              className="lf-label"
              style={{
                color: "var(--indigo-bright)",
                fontSize: 10,
                letterSpacing: "0.14em",
                background: "color-mix(in srgb, var(--indigo) 14%, transparent)",
                padding: "3px 9px",
                borderRadius: 99,
                border: "1px solid color-mix(in srgb, var(--indigo) 30%, transparent)",
              }}
            >
              ✦ AI ASSESSMENT ENGINE
            </span>
          </div>

          <div style={{ display: "flex", gap: 40, flexWrap: "wrap", alignItems: "flex-start" }}>
            {/* Left: description + readiness ring */}
            <div style={{ flex: "1 1 220px", minWidth: 200 }}>
              <h3 className="geist" style={{ fontSize: 18, fontWeight: 700, marginBottom: 6 }}>
                Predicting Your JEE Score
              </h3>
              <p className="dim body-sm" style={{ lineHeight: 1.6, marginBottom: 20, maxWidth: 320 }}>
                Based on your syllabus mastery across all three subjects. Score predictions use a
                non-linear scaling formula calibrated to actual JEE Mains candidate distributions.
                Keep mastering topics to lift your projection.
              </p>

              {/* Readiness ring */}
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ position: "relative", width: 88, height: 88, flex: "none" }}>
                  <svg width="88" height="88" viewBox="0 0 88 88">
                    <circle cx="44" cy="44" r="36" stroke="var(--surface-3)" strokeWidth="7" fill="transparent" />
                    <circle
                      cx="44" cy="44" r="36"
                      stroke="url(#readGrad)"
                      strokeWidth="7"
                      fill="transparent"
                      strokeDasharray={2 * Math.PI * 36}
                      strokeDashoffset={2 * Math.PI * 36 * (1 - (data.jee_readiness ?? 0) / 100)}
                      strokeLinecap="round"
                      transform="rotate(-90 44 44)"
                    />
                    <defs>
                      <linearGradient id="readGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="var(--indigo)" />
                        <stop offset="100%" stopColor="var(--success-clr)" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <div style={{
                    position: "absolute", top: 0, left: 0, width: "100%", height: "100%",
                    display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column",
                  }}>
                    <span className="lf-mono" style={{ fontSize: 17, fontWeight: 800 }}>
                      {Math.round(data.jee_readiness ?? 0)}%
                    </span>
                  </div>
                </div>
                <div>
                  <div style={{ fontSize: 12, textTransform: "uppercase", letterSpacing: "0.07em", color: "var(--text-faint)", marginBottom: 2 }}>
                    JEE Readiness
                  </div>
                  <div className="faint" style={{ fontSize: 11, lineHeight: 1.5 }}>
                    Weighted composite of mastery,<br />accuracy &amp; syllabus coverage
                  </div>
                </div>
              </div>
            </div>

            {/* Centre: Big score */}
            <div style={{ flex: "0 0 auto", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "0 8px" }}>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-faint)", marginBottom: 4 }}>
                Predicted Score
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 4 }}>
                <span
                  className="lf-mono"
                  style={{
                    fontSize: 56,
                    fontWeight: 900,
                    lineHeight: 1,
                    background: "linear-gradient(135deg, var(--success-clr), #22d3ee)",
                    WebkitBackgroundClip: "text",
                    WebkitTextFillColor: "transparent",
                    filter: "drop-shadow(0 0 14px rgba(74,222,128,0.35))",
                  }}
                >
                  {data.predicted_jee_score ?? 0}
                </span>
                <span className="faint" style={{ fontSize: 20, fontWeight: 400 }}>/&nbsp;300</span>
              </div>
              {/* Progress bar */}
              <div style={{ width: 160, height: 5, background: "var(--surface-3)", borderRadius: 99, marginTop: 12, overflow: "hidden" }}>
                <div style={{
                  height: "100%",
                  width: `${Math.min(100, ((data.predicted_jee_score ?? 0) / 300) * 100)}%`,
                  background: "linear-gradient(90deg, var(--indigo), var(--success-clr))",
                  borderRadius: 99,
                  boxShadow: "0 0 8px rgba(74,222,128,0.5)",
                  transition: "width 0.8s ease",
                }} />
              </div>
              <div className="faint" style={{ fontSize: 11, marginTop: 7, letterSpacing: "0.04em" }}>
                {(() => {
                  const score = data.predicted_jee_score ?? 0;
                  if (score >= 220) return "🏆 Top 1% territory";
                  if (score >= 180) return "🥇 Top 5% range";
                  if (score >= 140) return "🥈 Top 15% range";
                  if (score >= 100) return "🥉 Top 30% range";
                  return "📈 Keep mastering to climb";
                })()}
              </div>
            </div>

            {/* Right: Subject breakdown */}
            <div style={{ flex: "1 1 200px", minWidth: 180 }}>
              <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.08em", color: "var(--text-faint)", marginBottom: 12 }}>
                Subject Breakdown (out of 100)
              </div>
              {(
                [
                  { label: "Physics", key: "physics", color: "#818cf8", glow: "rgba(129,140,248,0.4)" },
                  { label: "Chemistry", key: "chemistry", color: "#34d399", glow: "rgba(52,211,153,0.4)" },
                  { label: "Maths", key: "maths", color: "#f59e0b", glow: "rgba(245,158,11,0.4)" },
                ] as const
              ).map(({ label, key, color, glow }) => {
                const score = data.subject_score_breakdown?.[key] ?? 0;
                return (
                  <div key={key} style={{ marginBottom: 14 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                      <span style={{ fontSize: 13, fontWeight: 500 }}>{label}</span>
                      <span className="lf-mono" style={{ fontSize: 13, color }}>{score.toFixed(1)}</span>
                    </div>
                    <div style={{ height: 6, background: "var(--surface-3)", borderRadius: 99, overflow: "hidden" }}>
                      <div style={{
                        height: "100%",
                        width: `${Math.min(100, score)}%`,
                        background: color,
                        borderRadius: 99,
                        boxShadow: `0 0 8px ${glow}`,
                        transition: "width 1s ease",
                      }} />
                    </div>
                  </div>
                );
              })}
              <div className="faint" style={{ fontSize: 10, marginTop: 6, lineHeight: 1.55 }}>
                Non-linear formula · JEE Mains negative marking modelled
              </div>
            </div>
          </div>
        </div>
      </section>


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
