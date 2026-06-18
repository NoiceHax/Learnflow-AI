"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { LayoutDashboard, BookOpen, BarChart3, User } from "lucide-react";
import { Brand } from "@/components/brand";
import { PageSkeleton } from "@/components/page-skeleton";
import { SocratesProvider } from "@/components/socrates-context";
import { SocratesWidget } from "@/components/socrates-widget";
import { useAuth } from "@/lib/auth";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/lessons", label: "Lessons", icon: BookOpen },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/profile", label: "Profile", icon: User },
];

function Loading() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <div className="topnav">
        <div className="app-container">
          <Brand />
          <div className="lf-row" style={{ gap: 8 }}>
            <div className="skel" style={{ height: 32, width: 88, borderRadius: 8 }} />
            <div className="skel" style={{ height: 32, width: 88, borderRadius: 8 }} />
            <div className="skel" style={{ height: 32, width: 88, borderRadius: 8 }} />
          </div>
        </div>
      </div>
      <main className="flex-1">
        <div className="app-container pt-9 md:pt-12">
          <PageSkeleton variant="shell" />
        </div>
      </main>
    </div>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (loading) return;
    if (!user) {
      router.replace("/login");
      return;
    }
    if (!user.onboarded) {
      router.replace("/exam/assessment");
    }
  }, [user, loading, pathname, router]);

  if (loading || !user) return <Loading />;

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");

  return (
    <SocratesProvider>
      <div className="flex min-h-screen flex-col bg-background">
        {/* desktop top nav */}
        <nav className="topnav">
          <div className="app-container">
            <Link href="/dashboard" aria-label="LEARNFLOW AI home">
              <Brand />
            </Link>
            <div className="navlinks">
              {NAV.map((n) => (
                <Link key={n.href} href={n.href} className={"navlink" + (isActive(n.href) ? " active" : "")}>
                  {n.label}
                </Link>
              ))}
            </div>
          </div>
        </nav>

        <main className="flex-1 pb-24 md:pb-16">
          <div className="app-container pt-9 md:pt-12">{children}</div>
        </main>

        {/* mobile bottom nav */}
        <nav className="botnav">
          {NAV.map((n) => (
            <Link key={n.href} href={n.href} className={isActive(n.href) ? "active" : ""}>
              <n.icon size={21} />
              <span>{n.label}</span>
            </Link>
          ))}
        </nav>
      </div>
      <SocratesWidget />
    </SocratesProvider>
  );
}
