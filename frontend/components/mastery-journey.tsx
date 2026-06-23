"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Check,
  Lock,
  AlertTriangle,
  ZoomIn,
  ZoomOut,
  Maximize2,
  BookOpen,
  PencilLine,
  X,
} from "lucide-react";
import type { JourneyNode, MasteryJourney } from "@/lib/types";

const NODE_W = 196;
const NODE_H = 84;
const GAP_X = 88;
const GAP_Y = 96;
const COLS = 5;
const PAD = 48;

const STATE_STYLES: Record<
  JourneyNode["state"],
  { stroke: string; fill: string; glow: string; text: string; badge: string }
> = {
  mastered: {
    stroke: "var(--success-clr)",
    fill: "rgba(74,222,128,0.12)",
    glow: "rgba(74,222,128,0.35)",
    text: "var(--success-clr)",
    badge: "Mastered",
  },
  in_progress: {
    stroke: "var(--indigo-bright)",
    fill: "rgba(99,102,241,0.16)",
    glow: "rgba(192,193,255,0.45)",
    text: "var(--indigo-bright)",
    badge: "Currently Learning",
  },
  revision: {
    stroke: "var(--warning-clr)",
    fill: "rgba(255,183,131,0.14)",
    glow: "rgba(255,183,131,0.4)",
    text: "var(--warning-clr)",
    badge: "Needs Revision",
  },
  locked: {
    stroke: "var(--text-faint)",
    fill: "var(--surface-2)",
    glow: "transparent",
    text: "var(--text-faint)",
    badge: "Locked",
  },
  available: {
    stroke: "var(--text-dim)",
    fill: "var(--surface-1)",
    glow: "transparent",
    text: "var(--text-dim)",
    badge: "Up Next",
  },
};

function layoutNodes(nodes: JourneyNode[]) {
  return nodes.map((node, i) => {
    const row = Math.floor(i / COLS);
    let col = i % COLS;
    if (row % 2 === 1) col = COLS - 1 - col;
    const x = PAD + col * (NODE_W + GAP_X);
    const y = PAD + row * (NODE_H + GAP_Y);
    return { node, x, y, cx: x + NODE_W / 2, cy: y + NODE_H / 2 };
  });
}

function edgePath(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  row1: number,
  row2: number
): string {
  if (row1 === row2) {
    const mx = (x1 + x2) / 2;
    return `M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}`;
  }
  const dy = (y2 - y1) * 0.55;
  return `M ${x1} ${y1} C ${x1} ${y1 + dy}, ${x2} ${y2 - dy}, ${x2} ${y2}`;
}

function NodeIcon({ state }: { state: JourneyNode["state"] }) {
  if (state === "mastered") return <Check size={14} strokeWidth={2.5} />;
  if (state === "locked") return <Lock size={13} />;
  if (state === "revision") return <AlertTriangle size={14} />;
  return null;
}

function DetailPanel({ node, onClose }: { node: JourneyNode; onClose: () => void }) {
  const d = node.detail;
  const style = STATE_STYLES[node.state];

  return (
    <div className="journey-panel fade-in">
      <div className="between" style={{ marginBottom: 16 }}>
        <div>
          <div className="lf-label" style={{ color: style.text }}>
            {node.inserted ? "Adaptive insert" : node.subtitle}
          </div>
          <h3 className="title" style={{ marginTop: 6, fontSize: 20 }}>
            {node.label}
          </h3>
        </div>
        <button className="navlink" onClick={onClose} aria-label="Close panel">
          <X size={18} />
        </button>
      </div>

      <div className="journey-panel-grid">
        <Metric label="Mastery" value={`${Math.round(node.mastery)}%`} accent={style.text} />
        <Metric label="Quiz attempts" value={String(d.quiz_attempts)} />
        <Metric label="Average score" value={d.average_score != null ? `${d.average_score}%` : "-"} />
        <Metric label="Time spent" value={d.time_spent_minutes > 0 ? `${d.time_spent_minutes} min` : "-"} />
      </div>

      {d.weak_concepts.length > 0 && (
        <div style={{ marginTop: 18 }}>
          <div className="lf-label" style={{ marginBottom: 8 }}>
            Weak concepts
          </div>
          <div className="lf-row" style={{ gap: 8, flexWrap: "wrap" }}>
            {d.weak_concepts.map((w) => (
              <span key={w.concept} className="chip" style={{ fontSize: 11, color: "var(--warning-clr)" }}>
                {w.concept} · {w.mastery}%
              </span>
            ))}
          </div>
        </div>
      )}

      {d.common_mistakes.length > 0 && (
        <div style={{ marginTop: 18 }}>
          <div className="lf-label" style={{ marginBottom: 8 }}>
            Common mistakes
          </div>
          <ul className="faint body-sm" style={{ margin: 0, paddingLeft: 18, lineHeight: 1.55 }}>
            {d.common_mistakes.map((m, i) => (
              <li key={i}>{m}</li>
            ))}
          </ul>
        </div>
      )}

      <div
        className="body-sm"
        style={{
          marginTop: 20,
          padding: "14px 16px",
          borderRadius: "var(--radius-md)",
          background: "var(--surface-2)",
          borderLeft: `3px solid ${style.stroke}`,
          lineHeight: 1.55,
        }}
      >
        <span className="lf-label" style={{ display: "block", marginBottom: 6 }}>
          Recommendation
        </span>
        {d.recommendation}
      </div>

      {node.state !== "locked" && (
        <div className="lf-row" style={{ gap: 10, marginTop: 22, flexWrap: "wrap" }}>
          <Link href={`/lessons/${node.chapter_id}`} className="btn btn-quiet btn-sm">
            <BookOpen size={15} /> Study
          </Link>
          <Link href={`/exam/quiz/${node.chapter_id}?mode=final`} className="btn btn-solid btn-sm">
            <PencilLine size={15} /> Final quiz
          </Link>
          <Link href={`/exam/quiz/${node.chapter_id}?mode=practice`} className="btn btn-quiet btn-sm">
            <PencilLine size={15} /> Practice
          </Link>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: string }) {
  return (
    <div className="journey-metric">
      <div className="lf-mono geist" style={{ fontSize: 22, fontWeight: 700, color: accent || "var(--text)" }}>
        {value}
      </div>
      <div className="faint" style={{ fontSize: 11.5, marginTop: 4 }}>
        {label}
      </div>
    </div>
  );
}

export function MasteryJourneyMap({ journey }: { journey: MasteryJourney }) {
  const [selected, setSelected] = useState<JourneyNode | null>(null);
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const [isDragging, setIsDragging] = useState(false);
  const drag = useRef<{ px: number; py: number; tx: number; ty: number } | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const positioned = useMemo(() => layoutNodes(journey.nodes), [journey.nodes]);

  const positions = useMemo(() => {
    const m = new Map<string, { x: number; y: number; cx: number; cy: number; row: number }>();
    positioned.forEach(({ node, x, y, cx, cy }, i) => {
      m.set(node.id, { x, y, cx, cy, row: Math.floor(i / COLS) });
    });
    return m;
  }, [positioned]);

  const rows = Math.max(1, Math.ceil(journey.nodes.length / COLS));
  const canvasW = PAD * 2 + COLS * NODE_W + (COLS - 1) * GAP_X;
  const canvasH = PAD * 2 + rows * NODE_H + (rows - 1) * GAP_Y;

  useEffect(() => {
    if (!journey.focus_node_id) return;
    const pos = positions.get(journey.focus_node_id);
    const el = containerRef.current;
    if (!pos || !el) return;
    const vw = el.clientWidth;
    const focusX = pos.cx * transform.scale;
    setTransform((t) => ({
      ...t,
      x: vw / 2 - focusX,
      y: 40,
    }));
  }, [journey.focus_node_id, positions]);

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.92 : 1.08;
      setTransform((t) => ({ ...t, scale: Math.min(1.6, Math.max(0.45, t.scale * delta)) }));
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  const onPointerDown = (e: React.PointerEvent) => {
    if ((e.target as HTMLElement).closest(".journey-node")) return;
    drag.current = { px: e.clientX, py: e.clientY, tx: transform.x, ty: transform.y };
    setIsDragging(true);
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
  };

  const onPointerMove = (e: React.PointerEvent) => {
    const d = drag.current;
    if (!d) return;
    const dx = e.clientX - d.px;
    const dy = e.clientY - d.py;
    setTransform((t) => ({
      ...t,
      x: d.tx + dx,
      y: d.ty + dy,
    }));
  };

  const onPointerUp = () => {
    drag.current = null;
    setIsDragging(false);
  };

  if (journey.nodes.length === 0) {
    return (
      <div className="surface pad" style={{ textAlign: "center" }}>
        <p className="body-lg dim">Complete your initial assessment to unlock your Mastery Journey.</p>
        <Link href="/exam/assessment" className="btn btn-solid" style={{ marginTop: 16 }}>
          Start assessment
        </Link>
      </div>
    );
  }

  return (
    <div className="journey-wrap">
      <div className="journey-toolbar between">
        <div className="lf-row" style={{ gap: 16, flexWrap: "wrap" }}>
          <Legend dot="var(--success-clr)" label="Mastered" />
          <Legend dot="var(--indigo-bright)" label="In progress" />
          <Legend dot="var(--warning-clr)" label="Needs revision" />
          <Legend dot="var(--text-faint)" label="Locked" />
        </div>
        <div className="lf-row" style={{ gap: 6 }}>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setTransform((t) => ({ ...t, scale: Math.min(1.6, t.scale * 1.12) }))}
            aria-label="Zoom in"
          >
            <ZoomIn size={15} />
          </button>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setTransform((t) => ({ ...t, scale: Math.max(0.45, t.scale * 0.88) }))}
            aria-label="Zoom out"
          >
            <ZoomOut size={15} />
          </button>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setTransform({ x: 0, y: 0, scale: 1 })}
            aria-label="Reset view"
          >
            <Maximize2 size={15} />
          </button>
        </div>
      </div>

      <div className={`journey-stage-row${selected && selected.state !== "locked" ? " has-panel" : ""}`}>
        <div
          ref={containerRef}
          className="journey-canvas scroll"
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerLeave={onPointerUp}
        >
          <svg
            width={canvasW}
            height={canvasH}
            style={{
              transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
              transformOrigin: "0 0",
              transition: isDragging ? "none" : "transform 0.35s var(--ease)",
            }}
          >
            <defs>
              <linearGradient id="pathGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="var(--indigo-deep)" stopOpacity="0.2" />
                <stop offset="50%" stopColor="var(--indigo-bright)" stopOpacity="0.55" />
                <stop offset="100%" stopColor="var(--indigo-deep)" stopOpacity="0.2" />
              </linearGradient>
            </defs>

            {journey.edges.map((e, i) => {
              const a = positions.get(e.from);
              const b = positions.get(e.to);
              if (!a || !b) return null;
              let x1: number, y1: number, x2: number, y2: number;
              if (a.row === b.row) {
                const leftToRight = a.x < b.x;
                x1 = leftToRight ? a.x + NODE_W : a.x;
                y1 = a.y + NODE_H / 2;
                x2 = leftToRight ? b.x : b.x + NODE_W;
                y2 = b.y + NODE_H / 2;
              } else {
                x1 = a.x + NODE_W / 2;
                y1 = a.y + NODE_H;
                x2 = b.x + NODE_W / 2;
                y2 = b.y;
              }
              return (
                <path
                  key={`${e.from}-${e.to}`}
                  d={edgePath(x1, y1, x2, y2, a.row, b.row)}
                  fill="none"
                  stroke="url(#pathGrad)"
                  strokeWidth={2}
                  strokeLinecap="round"
                  className="journey-edge"
                  style={{ animationDelay: `${i * 0.06}s` }}
                />
              );
            })}

            {positioned.map(({ node, x, y }) => {
              const style = STATE_STYLES[node.state];
              const isFocus = node.id === journey.focus_node_id;
              const isSelected = selected?.id === node.id;
              const active = isFocus || isSelected;

              return (
                <g
                  key={node.id}
                  className="journey-node"
                  transform={`translate(${x}, ${y})`}
                  onClick={() => setSelected(node)}
                  style={{ cursor: node.state === "locked" ? "not-allowed" : "pointer" }}
                >
                  {node.state === "in_progress" && (
                    <rect
                      x={-4}
                      y={-4}
                      width={NODE_W + 8}
                      height={NODE_H + 8}
                      rx={14}
                      fill="none"
                      stroke={style.stroke}
                      strokeWidth={1.5}
                      className="journey-pulse-ring"
                      opacity={0.7}
                    />
                  )}
                  <rect
                    width={NODE_W}
                    height={NODE_H}
                    rx={12}
                    fill={style.fill}
                    stroke={active ? style.stroke : "var(--hairline)"}
                    strokeWidth={active ? 2 : 1}
                    style={{
                      filter: active ? `drop-shadow(0 0 12px ${style.glow})` : undefined,
                      transition: "stroke 0.2s, filter 0.2s",
                    }}
                  />
                  {node.inserted && (
                    <rect x={12} y={-8} width={72} height={18} rx={4} fill="var(--warning-clr)" />
                  )}
                  {node.inserted && (
                    <text x={48} y={5} textAnchor="middle" fill="#1a1814" fontSize={9} fontWeight={600} fontFamily="var(--font-mono)">
                      ADAPTIVE
                    </text>
                  )}
                  <foreignObject x={14} y={14} width={NODE_W - 28} height={NODE_H - 28}>
                    <div>
                      <div className="lf-row between" style={{ gap: 8 }}>
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            justifyContent: "center",
                            width: 22,
                            height: 22,
                            borderRadius: 6,
                            background: style.fill,
                            color: style.text,
                            border: `1px solid ${style.stroke}`,
                          }}
                        >
                          <NodeIcon state={node.state} />
                        </span>
                        <span className="lf-mono faint" style={{ fontSize: 11 }}>
                          {node.state === "mastered"
                            ? `${Math.round(node.mastery)}%`
                            : node.state === "revision"
                              ? `${Math.round(node.mastery)}%`
                              : style.badge}
                        </span>
                      </div>
                      <div
                        className="geist"
                        style={{
                          fontWeight: 600,
                          fontSize: 13.5,
                          marginTop: 8,
                          lineHeight: 1.25,
                          color: node.state === "locked" ? "var(--text-faint)" : "var(--text)",
                          overflow: "hidden",
                          display: "-webkit-box",
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: "vertical",
                        }}
                      >
                        {node.label}
                      </div>
                      <div className="faint" style={{ fontSize: 10.5, marginTop: 4, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                        {node.type === "revision" ? "Inserted · revision" : node.subtitle}
                      </div>
                    </div>
                  </foreignObject>
                </g>
              );
            })}
          </svg>
        </div>

        {selected && selected.state !== "locked" && (
          <DetailPanel node={selected} onClose={() => setSelected(null)} />
        )}
      </div>
    </div>
  );
}

function Legend({ dot, label }: { dot: string; label: string }) {
  return (
    <span className="lf-row faint" style={{ gap: 7, fontSize: 11.5 }}>
      <span style={{ width: 8, height: 8, borderRadius: 99, background: dot }} />
      {label}
    </span>
  );
}
