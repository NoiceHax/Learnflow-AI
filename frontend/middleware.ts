import { NextResponse, type NextRequest } from "next/server";

/**
 * Subdomain routing.
 *
 * Deployed as two subdomains sharing one app + backend:
 *   app.astra.com   -> the learning platform (dashboard, lessons, analytics)
 *   exam.astra.com  -> the immersive exam environment (assessment, quizzes)
 *
 * When the request host starts with `exam.`, requests are rewritten into the
 * `/exam/*` route segment (its own bare, fullscreen layout). Locally, with no
 * DNS set up, just visit `/exam/...` directly; this middleware is a no-op.
 *
 * To try the real split locally, add to /etc/hosts:
 *   127.0.0.1 app.localhost
 *   127.0.0.1 exam.localhost
 * then open http://exam.localhost:3000
 */
export function middleware(req: NextRequest) {
  const host = req.headers.get("host") || "";
  const url = req.nextUrl;
  const isExamHost = host.startsWith("exam.");

  if (isExamHost) {
    // Already in the exam segment (or Next internals) -> leave it.
    if (url.pathname.startsWith("/exam") || url.pathname.startsWith("/_next") || url.pathname.startsWith("/api")) {
      return NextResponse.next();
    }
    // Bare root on the exam host -> the assessment entry point.
    const target = url.pathname === "/" ? "/exam/assessment" : `/exam${url.pathname}`;
    return NextResponse.rewrite(new URL(target, req.url));
  }

  // On the app host, keep students out of the raw /exam URLs only if you want a
  // hard split; we allow them locally so path-based access still works.
  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
