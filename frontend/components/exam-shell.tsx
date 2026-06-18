"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Maximize, Minimize, X, Lock, ShieldCheck, Expand } from "lucide-react";
import { Brand } from "@/components/brand";
import { QuizSkeleton } from "@/components/page-skeleton";
import { useAuth } from "@/lib/auth";

export function ExamShell({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [fs, setFs] = useState(false);
  // Fresh session id on every mount → the faux address bar reads like a new exam session.
  const [sessionId] = useState(() => Date.now().toString(36));

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [user, loading, router]);

  useEffect(() => {
    const onChange = () => setFs(Boolean(document.fullscreenElement));
    onChange();
    document.addEventListener("fullscreenchange", onChange);
    return () => document.removeEventListener("fullscreenchange", onChange);
  }, []);

  async function enter() {
    try {
      if (!document.fullscreenElement) await document.documentElement.requestFullscreen();
    } catch {
      /* some browsers block fullscreen; the gate remains and the student can exit */
    }
  }

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      /* non-fatal */
    }
  }

  async function exit() {
    if (document.fullscreenElement) await document.exitFullscreen().catch(() => {});
    router.push("/dashboard");
  }

  if (loading || !user) {
    return (
      <div className="exam-root">
        <div className="exam-address">
          <Lock size={12} style={{ color: "var(--text-faint)" }} />
          <div className="skel" style={{ height: 14, width: 200, borderRadius: 4 }} />
        </div>
        <header className="exam-head">
          <Brand />
          <div className="skel" style={{ height: 32, width: 80, borderRadius: 8 }} />
        </header>
        <div className="lf-wide" style={{ maxWidth: 1080, padding: "32px 24px 96px" }}>
          <QuizSkeleton />
        </div>
      </div>
    );
  }

  return (
    <div className="exam-root">
      {/* faux address bar: the exam subdomain */}
      <div className="exam-address">
        <Lock size={12} style={{ color: "var(--text-faint)" }} />
        <span className="lf-mono faint" style={{ fontSize: 12.5 }}>
          exam.learnflow.ai
          <span style={{ opacity: 0.5 }}>/session/{sessionId}</span>
        </span>
      </div>

      {/* slim exam header */}
      <header className="exam-head">
        <div className="lf-row" style={{ gap: 14 }}>
          <Brand />
          <span className="chip" style={{ background: "var(--indigo-wash)", color: "var(--indigo-bright)", fontSize: 11 }}>
            <ShieldCheck size={12} /> Exam Mode
          </span>
        </div>
        <div className="lf-row" style={{ gap: 6 }}>
          <button className="navlink" aria-label="Toggle fullscreen" onClick={toggleFullscreen} style={{ padding: 8 }}>
            {fs ? <Minimize size={16} /> : <Maximize size={16} />}
          </button>
          <button className="btn btn-quiet btn-sm" onClick={exit}>
            <X size={15} /> Exit
          </button>
        </div>
      </header>

      {/* exam body: inert + visually dimmed until fullscreen is engaged */}
      <div
        className="scroll"
        style={{
          flex: 1,
          overflowY: "auto",
          filter: fs ? "none" : "blur(6px)",
          pointerEvents: fs ? "auto" : "none",
          transition: "filter .3s var(--ease)",
        }}
        inert={!fs}
        aria-hidden={!fs}
      >
        <div className="lf-wide" style={{ maxWidth: 1080, padding: "32px 24px 96px" }}>
          {children}
        </div>
      </div>

      {!fs && <IntegrityGate onEnter={enter} onExit={exit} />}
    </div>
  );
}

/**
 * Fullscreen integrity gate. The exam only runs in fullscreen; otherwise this
 * blocking overlay states the academic-honesty expectation (a paraphrase, in
 * quotes) and offers the single way forward: enter fullscreen.
 */
function IntegrityGate({ onEnter, onExit }: { onEnter: () => void; onExit: () => void }) {
  return (
    <div
      role="alertdialog"
      aria-modal="true"
      aria-label="Fullscreen required"
      style={{
        position: "absolute",
        inset: 0,
        zIndex: 9999,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "24px",
        background: "color-mix(in srgb, var(--bg) 86%, transparent)",
        backdropFilter: "blur(8px)",
        WebkitBackdropFilter: "blur(8px)",
        animation: "fadeIn .35s var(--ease) both",
      }}
    >
      <div className="surface pad-l fade-in" style={{ maxWidth: 460, textAlign: "center", border: "1px solid var(--hairline)" }}>
        <div
          style={{
            width: 48,
            height: 48,
            margin: "0 auto",
            borderRadius: 14,
            background: "var(--indigo-wash)",
            color: "var(--indigo-bright)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Expand size={22} />
        </div>

        <div className="lf-label" style={{ marginTop: 22 }}>
          Academic Integrity
        </div>
        <h2 className="title" style={{ marginTop: 10 }}>
          The exam runs in fullscreen only
        </h2>

        <p className="body-lg dim" style={{ marginTop: 14, lineHeight: 1.6 }}>
          A distraction-free screen keeps the test fair for everyone. Before you begin, remember the
          one rule Socrates will not bend on:
        </p>

        <blockquote
          style={{
            margin: "20px 0 4px",
            padding: "16px 18px",
            borderRadius: "var(--radius-md)",
            background: "var(--surface-3)",
            fontStyle: "italic",
            fontSize: 16,
            lineHeight: 1.55,
            color: "var(--text)",
          }}
        >
          "Understanding earned honestly is the only kind worth having. Never trade it for a shortcut."
        </blockquote>

        <p className="faint body-sm" style={{ marginTop: 10 }}>
          Leaving fullscreen pauses the exam until you return.
        </p>

        <div className="lf-row" style={{ gap: 12, justifyContent: "center", marginTop: 26 }}>
          <button className="btn btn-ghost" onClick={onExit}>
            Not now
          </button>
          <button className="btn btn-solid" onClick={onEnter} autoFocus>
            <Maximize size={16} /> Enter fullscreen &amp; begin
          </button>
        </div>
      </div>
    </div>
  );
}

/** Request browser fullscreen. Call from a user gesture (e.g. a Begin button). */
export async function enterFullscreen() {
  try {
    if (!document.fullscreenElement) await document.documentElement.requestFullscreen();
  } catch {
    /* non-fatal */
  }
}
