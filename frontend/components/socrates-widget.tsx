"use client";

import { useEffect, useRef, useState } from "react";
import { Send, X } from "lucide-react";
import { useSocrates } from "@/components/socrates-context";
import { api, ApiError } from "@/lib/api";

interface Msg {
  role: "user" | "socrates";
  content: string;
  difficulty?: string;
  poweredBy?: string;
}

const QUIPS = [
  "Have you understood it, or memorized it?",
  "You are attacking the symptom, not the cause.",
  "Good. But why is it true?",
  "A formula recalled is not a truth understood.",
  "Slow down. Reason before you compute.",
];

const GENERIC_STARTERS = ["I don't understand this", "Give me a hint", "Am I memorizing this?"];

/** Classical philosopher portrait: face only (no raised hand). */
const SOCRATES_SVG = `
<svg viewBox="30 18 68 72" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" preserveAspectRatio="xMidYMid slice">
  <defs>
    <radialGradient id="s_bg" cx="42%" cy="32%" r="78%">
      <stop offset="0%" stop-color="#2a2620"/><stop offset="55%" stop-color="#1a1814"/><stop offset="100%" stop-color="#0d0c0a"/>
    </radialGradient>
    <linearGradient id="s_skin" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#c9a884"/><stop offset="55%" stop-color="#a8855f"/><stop offset="100%" stop-color="#6f553a"/>
    </linearGradient>
    <linearGradient id="s_hair" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#9a9085"/><stop offset="100%" stop-color="#544d44"/>
    </linearGradient>
  </defs>
  <rect x="30" y="18" width="68" height="72" fill="url(#s_bg)"/>
  <ellipse cx="62" cy="48" rx="22" ry="25" fill="url(#s_skin)"/>
  <path d="M62 24 C74 24 84 36 84 50 C84 62 76 72 64 72 C72 66 74 54 72 44 C70 34 66 28 62 24Z" fill="#5e472f" opacity="0.55"/>
  <path d="M50 44 C54 41 60 41 63 43" stroke="#4a3722" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M66 43 C70 41 75 42 78 45" stroke="#4a3722" stroke-width="2" fill="none" stroke-linecap="round"/>
  <ellipse cx="55" cy="48" rx="2.1" ry="1.7" fill="#34281a"/>
  <ellipse cx="71" cy="48" rx="2.1" ry="1.7" fill="#34281a"/>
  <path d="M49 42 C58 38 70 38 80 43" stroke="#3c2c1a" stroke-width="3" fill="none" opacity="0.35" stroke-linecap="round"/>
  <path d="M63 49 C61 55 59 59 56 61 C59 63 63 63 65 61" stroke="#6f553a" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <path d="M56 66 C60 64.5 66 64.5 70 66" stroke="#4a3722" stroke-width="1.8" fill="none" stroke-linecap="round"/>
  <g fill="url(#s_hair)">
    <circle cx="44" cy="38" r="8"/><circle cx="40" cy="48" r="7"/><circle cx="42" cy="30" r="7"/>
    <circle cx="52" cy="26" r="8"/><circle cx="62" cy="24" r="8"/><circle cx="72" cy="26" r="8"/>
    <circle cx="80" cy="32" r="7.5"/><circle cx="83" cy="42" r="7"/><circle cx="84" cy="51" r="6.5"/><circle cx="38" cy="40" r="5.5"/>
  </g>
  <path d="M48 40 C54 33 70 33 76 40 C72 37 52 37 48 40Z" fill="url(#s_skin)"/>
  <g fill="url(#s_hair)">
    <circle cx="50" cy="64" r="6.5"/><circle cx="58" cy="70" r="7"/><circle cx="66" cy="70" r="7"/>
    <circle cx="74" cy="64" r="6.5"/><circle cx="54" cy="72" r="6"/><circle cx="62" cy="74" r="6.5"/>
    <circle cx="70" cy="72" r="6"/><circle cx="47" cy="58" r="5.5"/><circle cx="77" cy="58" r="5.5"/><circle cx="62" cy="78" r="5"/>
  </g>
  <path d="M55 64 C60 67 66 67 71 64" stroke="#6b6359" stroke-width="3.5" fill="none" stroke-linecap="round"/>
  <ellipse cx="54" cy="34" rx="14" ry="10" fill="#fff" opacity="0.05"/>
</svg>`;

export function SocratesWidget() {
  const { context, open, setOpen, consumePending } = useSocrates();
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState<string | undefined>();
  const [sending, setSending] = useState(false);
  const [quip, setQuip] = useState(QUIPS[0]);
  const [lastPoweredBy, setLastPoweredBy] = useState<string | null>(null);
  const [rateLimited, setRateLimited] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const scroller = useRef<HTMLDivElement>(null);
  const pendingSent = useRef(false);

  // Cooldown timer for rate limiting
  useEffect(() => {
    if (cooldown <= 0) {
      setRateLimited(false);
      return;
    }
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  useEffect(() => {
    const t = setInterval(() => setQuip(QUIPS[Math.floor(Math.random() * QUIPS.length)]), 6000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    scroller.current?.scrollTo({ top: scroller.current.scrollHeight + 999, behavior: "smooth" });
  }, [messages, sending]);

  // When opened with a seeded question, send it automatically (once per open).
  useEffect(() => {
    if (!open) {
      pendingSent.current = false;
      return;
    }
    const pending = consumePending();
    if (!pending || pendingSent.current) return;
    pendingSent.current = true;
    void send(pending);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  async function send(text: string) {
    const message = text.trim();
    if (!message || sending || rateLimited) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: message }]);
    setSending(true);
    try {
      const res = await api.chat(message, sessionId, context ?? undefined);
      setSessionId(res.session_id);
      setLastPoweredBy(res.powered_by);
      setMessages((m) => [...m, { role: "socrates", content: res.reply, difficulty: res.difficulty, poweredBy: res.powered_by }]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setRateLimited(true);
        setCooldown(60);
        setMessages((m) => [
          ...m,
          {
            role: "socrates",
            content: "You've been asking excellent questions — but let's pause for a moment. True understanding needs time to settle. Take a breath, review what we've discussed, and return when you're ready.",
          },
        ]);
      } else {
        const detail =
          err instanceof Error && err.message
            ? err.message
            : "Cannot reach the server. Check that the backend is running and CORS is configured.";
        setMessages((m) => [...m, { role: "socrates", content: detail }]);
      }
    } finally {
      setSending(false);
    }
  }

  const starters = context?.section
    ? [`Explain "${context.section.slice(0, 26)}${context.section.length > 26 ? "…" : ""}"`, "Why does this matter?"]
    : context?.chapter
      ? [`Give me the intuition for ${context.chapter}.`, "What should I focus on?", "Am I memorizing this?"]
      : GENERIC_STARTERS;

  const chips = [context?.subject, context?.chapter, context?.section].filter(Boolean) as string[];

  return (
    <>
      {open && (
        <div className="socrates-panel" role="dialog" aria-label="Socrates dialogue">
          <div className="between" style={{ flexShrink: 0, padding: "16px 18px 12px" }}>
            <div className="lf-row" style={{ gap: 10 }}>
              <span style={{ width: 7, height: 7, borderRadius: 99, background: "var(--indigo)" }} />
              <span className="geist" style={{ fontWeight: 600, fontSize: 14, letterSpacing: "-0.01em" }}>
                Socrates
              </span>
              {lastPoweredBy === "nvidia" && (
                <span style={{
                  fontSize: 9,
                  fontWeight: 700,
                  letterSpacing: "0.1em",
                  textTransform: "uppercase",
                  padding: "2px 7px",
                  borderRadius: 99,
                  background: "color-mix(in srgb, var(--indigo) 14%, transparent)",
                  color: "var(--indigo-bright)",
                  border: "1px solid color-mix(in srgb, var(--indigo) 30%, transparent)",
                }}>
                  ✦ Live AI
                </span>
              )}
            </div>
            <button className="navlink" aria-label="Close Socrates" onClick={() => setOpen(false)}>
              <X size={16} />
            </button>
          </div>

          {chips.length > 0 && (
            <div className="lf-row" style={{ flexShrink: 0, gap: 6, padding: "0 18px 12px", flexWrap: "wrap" }}>
              {chips.map((c, i) => (
                <span key={i} className="chip" style={{ fontSize: 11, padding: "3px 9px" }}>
                  {c}
                </span>
              ))}
            </div>
          )}

          <div
            ref={scroller}
            className="socrates-messages scroll"
            style={{
              flex: 1,
              minHeight: 0,
              overflowY: "auto",
              overflowX: "hidden",
              padding: "6px 18px 10px",
              display: "flex",
              flexDirection: "column",
              gap: 16,
            }}
          >
            {messages.length === 0 && !sending && (
              <div className="faint body-sm" style={{ lineHeight: 1.6, paddingTop: 8 }}>
                {context?.chapter
                  ? `I already know you are on ${context.chapter}. So what, precisely, are you trying to understand?`
                  : "Ask a concept, a problem, or a formula. I will guide you to it, not hand it to you."}
              </div>
            )}
            {messages.map((m, i) =>
              m.role === "user" ? (
                <div
                  key={i}
                  className="msg-user fade-in"
                  style={{ maxWidth: "82%", padding: "9px 13px", borderRadius: 12, fontSize: 14, lineHeight: 1.45 }}
                >
                  {m.content}
                </div>
              ) : (
                <div key={i} className="msg-soc fade-in" style={{ maxWidth: "94%" }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: 5,
                    }}
                  >
                    <span
                      className="faint"
                      style={{ fontSize: 10.5, letterSpacing: "0.12em", textTransform: "uppercase" }}
                    >
                      Socrates asks
                    </span>
                    {m.difficulty && (
                      <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
                        <span
                          style={{
                            display: "inline-flex",
                            alignItems: "center",
                            gap: 4,
                            fontSize: 9.5,
                            fontWeight: 700,
                            padding: "3px 8px",
                            borderRadius: 99,
                            letterSpacing: "0.06em",
                            textTransform: "uppercase",
                            background:
                              m.difficulty === "Beginner"
                                ? "color-mix(in srgb, #4ade80 18%, transparent)"
                                : m.difficulty === "Advanced"
                                  ? "color-mix(in srgb, #f87171 18%, transparent)"
                                  : "color-mix(in srgb, #fbbf24 18%, transparent)",
                            color:
                              m.difficulty === "Beginner"
                                ? "#4ade80"
                                : m.difficulty === "Advanced"
                                  ? "#f87171"
                                  : "#fbbf24",
                            border: `1px solid ${
                              m.difficulty === "Beginner"
                                ? "rgba(74,222,128,0.3)"
                                : m.difficulty === "Advanced"
                                  ? "rgba(248,113,113,0.3)"
                                  : "rgba(251,191,36,0.3)"
                            }`,
                          }}
                        >
                          <span>
                            {m.difficulty === "Beginner" ? "◆" : m.difficulty === "Advanced" ? "★" : "◈"}
                          </span>
                          AI · {m.difficulty}
                        </span>
                      </div>
                    )}
                  </div>
                  {m.difficulty && (
                    <div
                      style={{
                        fontSize: 10,
                        color: "var(--text-faint)",
                        marginBottom: 5,
                        fontStyle: "italic",
                        letterSpacing: "0.01em",
                      }}
                    >
                      {m.difficulty === "Beginner"
                        ? "Concept explained with intuition & simple terms"
                        : m.difficulty === "Advanced"
                          ? "Rigorous treatment with derivations & edge cases"
                          : "Practical application with conceptual depth"}
                    </div>
                  )}

                  <div
                    style={{ fontSize: 14.5, lineHeight: 1.55, whiteSpace: "pre-line", color: "var(--text)" }}
                  >
                    {m.content}
                  </div>
                </div>
              )
            )}
            {sending && (
              <div className="fade-in" style={{ maxWidth: "92%" }}>
                <div
                  className="faint"
                  style={{ fontSize: 10.5, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 7 }}
                >
                  Socrates considers
                </div>
                <div className="stack-8" style={{ maxWidth: 220 }}>
                  <div className="skel" style={{ height: 12, width: "100%" }} />
                  <div className="skel" style={{ height: 12, width: "80%" }} />
                  <div className="skel" style={{ height: 12, width: "55%" }} />
                </div>
              </div>
            )}
          </div>

          <div
            className="lf-row no-scrollbar"
            style={{ flexShrink: 0, gap: 6, padding: "4px 18px 10px", overflowX: "auto", overflowY: "hidden" }}
          >
            {starters.map((s, i) => (
              <button
                key={i}
                className="chip"
                onClick={() => send(s)}
                disabled={rateLimited}
                style={{
                  cursor: rateLimited ? "not-allowed" : "pointer",
                  whiteSpace: "nowrap",
                  flex: "none",
                  opacity: rateLimited ? 0.4 : 1,
                }}
              >
                {s}
              </button>
            ))}
          </div>

          {rateLimited ? (
            <div style={{
              flexShrink: 0,
              padding: "12px 16px 16px",
              display: "flex",
              flexDirection: "column",
              gap: 6,
            }}>
              <div style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
                padding: "10px 14px",
                borderRadius: 10,
                background: "color-mix(in srgb, #fbbf24 10%, var(--surface-3))",
                border: "1px solid color-mix(in srgb, #fbbf24 25%, transparent)",
              }}>
                <span style={{ fontSize: 16 }}>⏳</span>
                <span style={{
                  flex: 1,
                  fontSize: 12,
                  color: "var(--text-faint)",
                  fontStyle: "italic",
                }}>
                  Socrates will return in {cooldown}s — reflect on what you&apos;ve learned
                </span>
              </div>
              <div style={{
                height: 3,
                borderRadius: 99,
                background: "var(--surface-3)",
                overflow: "hidden",
              }}>
                <div style={{
                  height: "100%",
                  width: `${Math.max(0, (cooldown / 60) * 100)}%`,
                  background: "linear-gradient(90deg, #fbbf24, #f59e0b)",
                  borderRadius: 99,
                  transition: "width 1s linear",
                }} />
              </div>
            </div>
          ) : (
            <div className="lf-row" style={{ flexShrink: 0, gap: 8, padding: "12px 16px 16px" }}>
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && input.trim()) send(input.trim());
                }}
                placeholder="Answer, or ask why…"
                style={{
                  flex: 1,
                  background: "var(--surface-3)",
                  border: 0,
                  borderRadius: 10,
                  color: "var(--text)",
                  padding: "11px 14px",
                  fontSize: 14,
                  fontFamily: "var(--font-sans)",
                  outline: "none",
                }}
              />
              <button
                className="btn btn-solid btn-sm"
                style={{ height: 40, width: 40, padding: 0 }}
                aria-label="Send message"
                disabled={!input.trim() || sending}
                onClick={() => input.trim() && send(input.trim())}
              >
                <Send size={17} />
              </button>
            </div>
          )}
        </div>
      )}

      <div className="socrates-fix">
        {!open && <div className="socrates-quip">“{quip}”</div>}
        <div
          className="socrates-portrait"
          role="button"
          tabIndex={0}
          aria-label="Open Socrates"
          onClick={() => setOpen(!open)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              setOpen(!open);
            }
          }}
          dangerouslySetInnerHTML={{ __html: SOCRATES_SVG }}
        />
        <span className="socrates-status" />
        <div
          style={{
            marginTop: 8,
            fontFamily: "var(--font-display)",
            fontSize: 11,
            letterSpacing: "0.14em",
            textTransform: "uppercase",
            color: "var(--text-faint)",
          }}
        >
          Socrates
        </div>
      </div>
    </>
  );
}
