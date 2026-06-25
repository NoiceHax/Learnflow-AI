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
import { ThemeToggle } from "@/components/theme-toggle";

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
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background animated glows */}
      <div className="bg-glow-container">
        <div 
          className="bg-glow-circle" 
          style={{ 
            top: -150, 
            left: "15%", 
            width: 500, 
            height: 500, 
            background: "radial-gradient(circle, rgba(99,102,241,0.18) 0%, transparent 70%)" 
          }} 
        />
        <div 
          className="bg-glow-circle" 
          style={{ 
            top: 200, 
            right: "10%", 
            width: 600, 
            height: 600, 
            background: "radial-gradient(circle, rgba(168,85,247,0.15) 0%, transparent 70%)",
            animationDelay: "-6s" 
          }} 
        />
      </div>

      <header className="topnav relative z-10">
        <div className="lf-wide">
          <Brand />
          <div className="lf-row" style={{ gap: 16 }}>
            <Link href="/login?mode=signin" className="navlink">
              Sign in
            </Link>
            <ThemeToggle />
            <Link href="/login?mode=signup" className="btn btn-solid btn-sm">
              Get started
            </Link>
          </div>
        </div>
      </header>

      <section style={{ borderBottom: "1px solid var(--hairline-soft)", position: "relative", zIndex: 1 }}>
        <div className="lf-wide" style={{ maxWidth: 880, textAlign: "center", padding: "112px 24px 120px" }}>
          <div
            className="chip animate-fade-in-up delay-100"
            style={{ margin: "0 auto 24px", display: "inline-flex" }}
          >
            <span style={{ width: 6, height: 6, borderRadius: 99, background: "var(--indigo-bright)" }} />
            Built for JEE Advanced · Grade 12
          </div>
          <h1 className="display animate-fade-in-up delay-200" style={{ fontSize: 60, maxWidth: 720, margin: "0 auto", lineHeight: 1.04 }}>
            A strict mentor that helps you <span className="accent">understand</span>, not memorize.
          </h1>
          <p className="body-lg dim animate-fade-in-up delay-300" style={{ maxWidth: 600, margin: "22px auto 0" }}>
            LEARNFLOW AI builds an adaptive path from your assessment, teaches with premium coaching
            material, and repairs weak foundations, guided every step by Socrates.
          </p>
          <div className="lf-row animate-fade-in-up delay-400" style={{ gap: 12, justifyContent: "center", marginTop: 34, flexWrap: "wrap" }}>
            <Link href="/login?mode=signup" className="btn btn-solid btn-lg">
              Start your assessment <ArrowRight size={16} />
            </Link>
            <Link href="/login?mode=signin" className="btn btn-quiet btn-lg">
              Sign in
            </Link>
          </div>
        </div>
      </section>

      <section className="lf-wide relative z-10" style={{ padding: "72px 24px" }}>
        <div className="lf-label animate-fade-in-up delay-500" style={{ textAlign: "center", marginBottom: 32 }}>
          Four subjects · the complete JEE Advanced syllabus
        </div>
        <div className="landing-grid-4 animate-fade-in-up delay-500">
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

      <section style={{ borderTop: "1px solid var(--hairline-soft)", position: "relative", zIndex: 10 }}>
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

      <footer style={{ borderTop: "1px solid var(--hairline-soft)", position: "relative", zIndex: 10 }}>
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
