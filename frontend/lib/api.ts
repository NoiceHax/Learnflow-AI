import type {
  AssessmentResult,
  ChatResponse,
  ChatSession,
  ChatTurn,
  Dashboard,
  LearningPath,
  Lesson,
  Mastery,
  Question,
  QuizResult,
  SocratesContextPayload,
  Subject,
  User,
} from "./types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

const TOKEN_KEY = "astra_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let res: Response;
  try {
    res = await fetch(`${API_URL}/api${path}`, { ...options, headers });
  } catch {
    throw new ApiError(0, "Cannot reach the Astra server. Is the backend running?");
  }

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  // auth
  signup: (name: string, email: string, password: string) =>
    request<{ token: string; user: User }>("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    }),
  login: (email: string, password: string) =>
    request<{ token: string; user: User }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),
  me: () => request<User>("/auth/me"),

  // catalog
  subjects: () => request<Subject[]>("/catalog/subjects"),

  // assessment
  assessmentQuestions: () => request<Question[]>("/assessment/questions"),
  submitAssessment: (answers: { question_id: string; answer: unknown }[], time_taken: number) =>
    request<AssessmentResult>("/assessment/submit", {
      method: "POST",
      body: JSON.stringify({ answers, time_taken }),
    }),

  // quiz: mode practice (missed questions) | final (chapter completion quiz)
  quizQuestions: (chapterId: string, count = 6, mode: "practice" | "final" = "final") =>
    request<Question[]>(`/quiz/${chapterId}/questions?count=${count}&mode=${mode}`),
  submitQuiz: (
    chapterId: string,
    answers: { question_id: string; answer: unknown }[],
    time_taken: number,
    mode: "practice" | "final" = "final",
  ) =>
    request<QuizResult>(`/quiz/${chapterId}/submit`, {
      method: "POST",
      body: JSON.stringify({ answers, time_taken, mode }),
    }),

  // learning path
  learningPath: () => request<LearningPath>("/learning-path"),
  regeneratePath: () => request<LearningPath>("/learning-path/regenerate", { method: "POST" }),

  // lessons
  lesson: (chapterId: string) => request<Lesson>(`/lessons/${chapterId}`),

  // mastery + dashboard
  mastery: () => request<Mastery[]>("/mastery"),
  dashboard: () => request<Dashboard>("/dashboard"),

  // socrates
  chat: (message: string, session_id?: string, context?: SocratesContextPayload) =>
    request<ChatResponse>("/socrates/chat", {
      method: "POST",
      body: JSON.stringify({ message, session_id, context, chapter_context: context?.chapter }),
    }),
  chatSessions: () => request<ChatSession[]>("/socrates/sessions"),
  chatHistory: (sessionId: string) => request<ChatTurn[]>(`/socrates/sessions/${sessionId}`),
};
