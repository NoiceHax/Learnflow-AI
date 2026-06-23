import Link from "next/link";
import {
  Atom,
  Sigma,
  FlaskConical,
  Hexagon,
  ArrowRight,
  ClipboardCheck,
  Route,
  BookOpen,
  MessageCircleQuestion,
  BarChart3,
} from "lucide-react";
import { Brand } from "@/components/brand";

const SUBJECTS = [
  { name: "Organic Chemistry", icon: FlaskConical, blurb: "GOC, hydrocarbons, carbonyls, amines & more." },
  { name: "Inorganic Chemistry", icon: Hexagon, blurb: "Bonding, coordination, p / d / f-block, analysis." },
  { name: "Advanced Physics", icon: Atom, blurb: "Mechanics to modern physics, the full syllabus." },
  { name: "Advanced Mathematics", icon: Sigma, blurb: "Algebra, calculus, vectors, probability & more." },
];

const FLOW = [
  { icon: ClipboardCheck, title: "Initial Assessment", text: "A fullscreen diagnostic across all four subjects builds your knowledge profile." },
  { icon: Route, title: "Adaptive Path", text: "The engine traces failures to their root and teaches the foundation first." },
  { icon: BookOpen, title: "Premium Lessons", text: "Theory, solved examples, formula sheets, common mistakes and PYQs." },
  { icon: MessageCircleQuestion, title: "Socrates", text: "A strict mentor who guides with questions instead of handing you answers." },
  { icon: BarChart3, title: "Adaptive Progress", text: "Mastery updates after every quiz; weak concepts keep resurfacing." },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="topnav">
        <div className="lf-wide">
          <Brand />
          <div className="lf-row" style={{ gap: 12 }}>
            <Link href="/login?mode=signin" className="navlink">
              Sign in
            </Link>
            <Link href="/login?mode=signup" className="btn btn-solid btn-sm">
              Get started
            </Link>
          </div>
        </div>
      </header>

      <section style={{ borderBottom: "1px solid var(--hairline-soft)" }}>
        <div className="lf-wide" style={{ maxWidth: 880, textAlign: "center", padding: "112px 24px 120px" }}>
          <div
            className="chip"
            style={{ margin: "0 auto 24px", display: "inline-flex" }}
          >
            <span style={{ width: 6, height: 6, borderRadius: 99, background: "var(--indigo-bright)" }} />
            Built for JEE Advanced · Grade 12
          </div>
          <h1 className="display" style={{ fontSize: 60, maxWidth: 720, margin: "0 auto", lineHeight: 1.04 }}>
            A strict mentor that helps you <span className="accent">understand</span>, not memorize.
          </h1>
          <p className="body-lg dim" style={{ maxWidth: 600, margin: "22px auto 0" }}>
            LEARNFLOW AI builds an adaptive path from your assessment, teaches with premium coaching
            material, and repairs weak foundations, guided every step by Socrates.
          </p>
          <div className="lf-row" style={{ gap: 12, justifyContent: "center", marginTop: 34, flexWrap: "wrap" }}>
            <Link href="/login?mode=signup" className="btn btn-solid btn-lg">
              Start your assessment <ArrowRight size={16} />
            </Link>
            <Link href="/login?mode=signin" className="btn btn-quiet btn-lg">
              Sign in
            </Link>
          </div>
        </div>
      </section>

      <section className="lf-wide" style={{ padding: "72px 24px" }}>
        <div className="lf-label" style={{ textAlign: "center", marginBottom: 32 }}>
          Four subjects · the complete JEE Advanced syllabus
        </div>
        <div className="landing-grid-4">
          {SUBJECTS.map((s) => (
            <div key={s.name} className="surface pad">
              <div
                style={{
                  width: 44,
                  height: 44,
                  borderRadius: 10,
                  background: "var(--surface-3)",
                  color: "var(--text)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                <s.icon size={22} />
              </div>
              <div className="geist" style={{ fontWeight: 600, fontSize: 16, marginTop: 16 }}>
                {s.name}
              </div>
              <p className="faint body-sm" style={{ marginTop: 6, lineHeight: 1.5 }}>
                {s.blurb}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section style={{ borderTop: "1px solid var(--hairline-soft)" }}>
        <div className="lf-wide" style={{ padding: "80px 24px" }}>
          <h2 className="headline" style={{ textAlign: "center" }}>
            A learning loop that moves the needle
          </h2>
          <div className="landing-grid-5" style={{ marginTop: 44 }}>
            {FLOW.map((f, i) => (
              <div key={f.title} className="surface pad">
                <div
                  style={{
                    width: 36,
                    height: 36,
                    borderRadius: 9,
                    background: "var(--indigo-wash)",
                    color: "var(--indigo-bright)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <f.icon size={18} />
                </div>
                <div className="lf-label" style={{ marginTop: 14 }}>
                  Step {i + 1}
                </div>
                <div className="geist" style={{ fontWeight: 600, marginTop: 6 }}>
                  {f.title}
                </div>
                <p className="faint body-sm" style={{ marginTop: 6, lineHeight: 1.5 }}>
                  {f.text}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer style={{ borderTop: "1px solid var(--hairline-soft)" }}>
        <div
          className="lf-wide between"
          style={{ padding: "32px 24px", flexWrap: "wrap", gap: 16 }}
        >
          <Brand />
          <p className="faint body-sm">
            © {new Date().getFullYear()} LEARNFLOW AI · An adaptive learning platform for JEE Advanced.
          </p>
        </div>
      </footer>
    </div>
  );
}
