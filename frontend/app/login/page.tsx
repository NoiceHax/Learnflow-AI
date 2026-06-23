"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { Brand } from "@/components/brand";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useAuth } from "@/lib/auth";

function LoginForm() {
  const { user, loading, login, signup } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const mode = searchParams.get("mode");
    if (mode === "signup" || mode === "signin") {
      setTab(mode);
    }
  }, [searchParams]);

  useEffect(() => {
    if (!loading && user) {
      router.replace(user.onboarded ? "/dashboard" : "/exam/assessment");
    }
  }, [user, loading, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();
    const trimmedName = name.trim();

    if (!trimmedEmail) {
      setError("Please enter your email address.");
      return;
    }
    if (!trimmedPassword) {
      setError("Please enter your password.");
      return;
    }
    if (trimmedPassword.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }
    if (tab === "signup" && !trimmedName) {
      setError("Please enter your full name.");
      return;
    }

    setBusy(true);
    try {
      const u =
        tab === "signin"
          ? await login(trimmedEmail, trimmedPassword)
          : await signup(trimmedName, trimmedEmail, trimmedPassword);
      router.replace(u.onboarded ? "/dashboard" : "/exam/assessment");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="relative flex min-h-screen items-center justify-center px-4">
        <div className="w-full max-w-md stack-16">
          <div className="skel" style={{ height: 32, width: 160, margin: "0 auto", borderRadius: 8 }} />
          <div className="skel" style={{ height: 380, borderRadius: 12 }} />
        </div>
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center px-4">
      <div className="relative w-full max-w-md">
        <div className="mb-6 flex justify-center">
          <Link href="/">
            <Brand />
          </Link>
        </div>
        <Card>
          <CardContent className="p-6">
            <Tabs value={tab} onValueChange={(v) => { setTab(v); setError(null); }}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="signin">Sign in</TabsTrigger>
                <TabsTrigger value="signup">Create account</TabsTrigger>
              </TabsList>

              <div className="mt-6">
                <h1 className="text-xl font-bold tracking-tight">
                  {tab === "signin" ? "Welcome back" : "Create your account"}
                </h1>
                <p className="mt-1 text-sm text-muted-foreground">
                  {tab === "signin"
                    ? "Sign in to continue your JEE Advanced prep."
                    : "Start with a short assessment to personalise your path."}
                </p>
              </div>

              <form onSubmit={handleSubmit} className="mt-5 space-y-4">
                {tab === "signup" && (
                  <div className="space-y-2">
                    <Label htmlFor="name">Full name</Label>
                    <Input
                      id="name"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="Aarav Sharma"
                      autoComplete="name"
                      required
                    />
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="At least 6 characters"
                    minLength={6}
                    required
                  />
                </div>

                {error && (
                  <p className="rounded-md bg-destructive/10 px-3 py-2 text-sm text-destructive">{error}</p>
                )}

                <Button type="submit" className="w-full" disabled={busy}>
                  {busy && <Loader2 className="size-4 animate-spin" />}
                  {tab === "signin" ? "Sign in" : "Create account & start"}
                </Button>
              </form>
            </Tabs>
          </CardContent>
        </Card>
        <p className="mt-4 text-center text-xs text-muted-foreground">
          By continuing you agree to use LEARNFLOW AI for JEE Advanced preparation.
        </p>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="relative flex min-h-screen items-center justify-center px-4">
          <div className="w-full max-w-md stack-16">
            <div className="skel" style={{ height: 32, width: 160, margin: "0 auto", borderRadius: 8 }} />
            <div className="skel" style={{ height: 380, borderRadius: 12 }} />
          </div>
        </div>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
