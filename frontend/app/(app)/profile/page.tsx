"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { LogOut, GraduationCap } from "lucide-react";
import { PageSkeleton } from "@/components/page-skeleton";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Dashboard } from "@/lib/types";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const [data, setData] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .dashboard()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <PageSkeleton variant="profile" />;
  }

  const initials = (user?.name ?? "")
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  const stats = [
    { label: "Overall progress", value: data ? `${data.overall_progress}%` : "-" },
    { label: "Accuracy", value: data ? `${data.accuracy}%` : "-" },
    { label: "Chapters mastered", value: data ? `${data.chapters_completed}` : "-" },
    { label: "Time invested", value: data ? `${data.time_spent_hours} h` : "-" },
  ];

  return (
    <div style={{ paddingBottom: 40 }}>
      <div className="lf-section" style={{ marginBottom: 40 }}>
        <div className="lf-label" style={{ marginBottom: 14 }}>
          Profile
        </div>
        <div className="lf-row" style={{ gap: 18 }}>
          <div
            className="geist"
            style={{
              width: 64,
              height: 64,
              borderRadius: 16,
              background: "var(--indigo-wash)",
              color: "var(--indigo-bright)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 22,
              fontWeight: 600,
            }}
          >
            {initials || <GraduationCap size={26} />}
          </div>
          <div>
            <h1 className="headline">{user?.name}</h1>
            <p className="faint" style={{ marginTop: 4 }}>
              {user?.email}
            </p>
          </div>
        </div>
      </div>

      <div className="lf-section">
        <div className="lf-label" style={{ marginBottom: 18 }}>
          Your numbers
        </div>
        <div className="profile-stats">
          {stats.map((s) => (
            <div key={s.label} className="surface pad">
              <div className="lf-mono geist" style={{ fontSize: 32, fontWeight: 700 }}>
                {s.value}
              </div>
              <div className="faint body-sm" style={{ marginTop: 4 }}>
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="lf-section">
        <div className="lf-label" style={{ marginBottom: 18 }}>
          Account
        </div>
        <div className="surface" style={{ overflow: "hidden" }}>
          <button className="lrow" style={{ borderRadius: 0, padding: "18px 22px" }} onClick={logout}>
            <div className="lf-row" style={{ gap: 14 }}>
              <span className="ic" style={{ color: "var(--error-clr)" }}>
                <LogOut size={18} />
              </span>
              <div className="geist" style={{ fontWeight: 500, fontSize: 15, color: "var(--error-clr)" }}>
                Log out
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
