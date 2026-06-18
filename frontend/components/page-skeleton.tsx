/** Shimmer skeleton placeholders. Use while auth or page data loads. */

type Variant = "shell" | "dashboard" | "lessons" | "lesson" | "quiz" | "analytics" | "profile";

export function PageSkeleton({ variant = "shell" }: { variant?: Variant }) {
  switch (variant) {
    case "dashboard":
      return <DashboardSkeleton />;
    case "lessons":
      return <LessonsSkeleton />;
    case "lesson":
      return <LessonSkeleton />;
    case "quiz":
      return <QuizSkeleton />;
    case "analytics":
      return <AnalyticsSkeleton />;
    case "profile":
      return <ProfileSkeleton />;
    default:
      return <ShellSkeleton />;
  }
}

function ShellSkeleton() {
  return (
    <div className="stack-24">
      <div className="skel" style={{ height: 36, width: "42%" }} />
      <div className="skel" style={{ height: 20, width: "28%" }} />
      <div className="dash-metrics">
        <div className="skel" style={{ height: 88, borderRadius: 12 }} />
        <div className="skel" style={{ height: 88, borderRadius: 12 }} />
        <div className="skel" style={{ height: 88, borderRadius: 12 }} />
      </div>
      <div className="skel" style={{ height: 320, borderRadius: 16 }} />
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="stack-24">
      <div className="skel" style={{ height: 40, width: "50%" }} />
      <div className="dash-metrics">
        <div className="skel" style={{ height: 88, borderRadius: 12 }} />
        <div className="skel" style={{ height: 88, borderRadius: 12 }} />
        <div className="skel" style={{ height: 88, borderRadius: 12 }} />
      </div>
      <div className="skel" style={{ height: 480, borderRadius: 16 }} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
        <div className="skel" style={{ height: 200, borderRadius: 12 }} />
        <div className="skel" style={{ height: 200, borderRadius: 12 }} />
      </div>
    </div>
  );
}

function LessonsSkeleton() {
  return (
    <div className="stack-24">
      <div className="skel" style={{ height: 32, width: 140 }} />
      <div className="skel" style={{ height: 18, width: 320 }} />
      <div className="lf-row" style={{ gap: 8, flexWrap: "wrap" }}>
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skel" style={{ height: 36, width: 148, borderRadius: 99 }} />
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 16 }}>
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="skel" style={{ height: 168, borderRadius: 12 }} />
        ))}
      </div>
    </div>
  );
}

function LessonSkeleton() {
  return (
    <div className="stack-24" style={{ maxWidth: 720 }}>
      <div className="skel" style={{ height: 32, width: 100 }} />
      <div className="between" style={{ flexWrap: "wrap", gap: 16 }}>
        <div className="stack-8" style={{ flex: 1 }}>
          <div className="skel" style={{ height: 36, width: "70%" }} />
          <div className="skel" style={{ height: 22, width: 160, borderRadius: 99 }} />
        </div>
        <div className="lf-row" style={{ gap: 8 }}>
          <div className="skel" style={{ height: 40, width: 130, borderRadius: 10 }} />
          <div className="skel" style={{ height: 40, width: 110, borderRadius: 10 }} />
        </div>
      </div>
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="skel" style={{ height: i === 0 ? 140 : 120, borderRadius: 12 }} />
      ))}
    </div>
  );
}

export function QuizSkeleton() {
  return (
    <div className="exam-grid">
      <div>
        <div className="between" style={{ flexWrap: "wrap", gap: 12, marginBottom: 28 }}>
          <div className="stack-8">
            <div className="skel" style={{ height: 28, width: 260 }} />
            <div className="skel" style={{ height: 16, width: 180 }} />
          </div>
          <div className="skel" style={{ height: 28, width: 72, borderRadius: 8 }} />
        </div>
        <div className="skel" style={{ height: 14, width: 120, marginBottom: 20 }} />
        <div className="skel" style={{ height: 72, width: "92%", marginBottom: 32 }} />
        <div className="stack-16">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skel" style={{ height: 52, borderRadius: 10 }} />
          ))}
        </div>
        <div className="between" style={{ marginTop: 40 }}>
          <div className="skel" style={{ height: 40, width: 110, borderRadius: 10 }} />
          <div className="lf-row" style={{ gap: 10 }}>
            <div className="skel" style={{ height: 40, width: 80, borderRadius: 10 }} />
            <div className="skel" style={{ height: 40, width: 100, borderRadius: 10 }} />
          </div>
        </div>
      </div>
      <div className="stack-8" style={{ minWidth: 200 }}>
        <div className="skel" style={{ height: 18, width: 100, marginBottom: 8 }} />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8 }}>
          {Array.from({ length: 10 }).map((_, i) => (
            <div key={i} className="skel" style={{ height: 36, borderRadius: 8 }} />
          ))}
        </div>
        <div className="skel" style={{ height: 6, borderRadius: 99, marginTop: 16 }} />
      </div>
    </div>
  );
}

function AnalyticsSkeleton() {
  return (
    <div className="stack-24">
      <div className="skel" style={{ height: 32, width: 160 }} />
      <div className="skel" style={{ height: 18, width: 340 }} />
      <div className="dash-metrics">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skel" style={{ height: 88, borderRadius: 12 }} />
        ))}
      </div>
      <div className="skel" style={{ height: 120, borderRadius: 12 }} />
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
        <div className="skel" style={{ height: 320, borderRadius: 12 }} />
        <div className="skel" style={{ height: 320, borderRadius: 12 }} />
      </div>
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div className="stack-24">
      <div className="lf-row" style={{ gap: 18 }}>
        <div className="skel" style={{ width: 64, height: 64, borderRadius: 16, flexShrink: 0 }} />
        <div className="stack-8" style={{ flex: 1 }}>
          <div className="skel" style={{ height: 28, width: 200 }} />
          <div className="skel" style={{ height: 16, width: 240 }} />
        </div>
      </div>
      <div className="profile-stats">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="skel" style={{ height: 96, borderRadius: 12 }} />
        ))}
      </div>
      <div className="skel" style={{ height: 72, borderRadius: 12 }} />
    </div>
  );
}
