export interface User {
  id: string;
  name: string;
  email: string;
  onboarded: boolean;
}

export interface Chapter {
  id: string;
  chapter_name: string;
  slug: string;
  subject_id: string;
  prerequisite_id: string | null;
  order_index: number;
  jee_weightage: number;
  description: string;
  unlocked?: boolean;
}

export interface Subject {
  id: string;
  name: string;
  slug: string;
  icon: string;
  chapters: Chapter[];
}

export type QuestionType =
  | "single_correct"
  | "multiple_correct"
  | "integer"
  | "numerical";

export interface QuestionOption {
  id: string;
  text: string;
}

export interface Question {
  id: string;
  subject: string;
  chapter: string;
  chapter_id: string;
  difficulty: string;
  concept: string;
  jee_weightage: number;
  type: QuestionType;
  prompt: string;
  options: QuestionOption[] | null;
  unit: string | null;
  ai_generated?: boolean;
  is_pyq?: boolean;
  pyq_year?: number | null;
  pyq_exam?: string | null;
}

export type AnswerValue = number | number[] | string | null;

export interface GradedQuestion {
  question_id: string;
  concept: string;
  chapter: string;
  correct: boolean;
  your_answer: AnswerValue;
  correct_answer: AnswerValue;
  solution: string;
}

export interface AdaptiveSummary {
  retired_count: number;
  replacements_generated: number;
  weak_concepts_hit: string[];
}

export interface QuizResult {
  score: number;
  accuracy: number;
  total_questions: number;
  correct_count: number;
  time_taken: number;
  weak_concepts: string[];
  graded: GradedQuestion[];
  adaptive?: AdaptiveSummary | null;
  chapter_mastered?: boolean;
}

export interface AssessmentResult {
  id: string;
  score: number;
  chapter_scores: Record<string, number>;
  subject_scores: Record<string, number>;
  knowledge_map: { chapter: string; slug: string; subject: string; score: number }[];
  total_questions: number;
  correct_count: number;
}

export interface PathItem {
  chapter_id: string;
  chapter_name: string;
  slug: string;
  subject: string;
  position: number;
  status: "locked" | "available" | "in_progress" | "completed" | "mastered";
  is_weak: boolean;
  reason: string;
  mastery: number;
  jee_weightage: number;
}

export interface LearningPath {
  items: PathItem[];
  current_chapter: string | null;
  next_chapter: string | null;
}

export interface Lesson {
  id: string;
  chapter_id: string;
  chapter: string;
  generated_by_ai: boolean;
  content: {
    theory: string;
    key_concepts: string[];
    formulas: { name: string; expr: string }[];
    examples: { problem: string; solution: string }[];
    common_mistakes: string[];
    pyq_highlights: string[];
    practice: { easy: string; medium: string; advanced: string };
  };
}

export interface ExamHistoryItem {
  kind: "assessment" | "final_quiz";
  id: string;
  title: string;
  chapter: string | null;
  chapter_id: string | null;
  subject: string | null;
  score: number;
  accuracy: number;
  correct_count: number;
  total_questions: number;
  time_taken: number | null;
  passed: boolean | null;
  timestamp: string;
}

export interface ExamReport {
  kind: "assessment" | "final_quiz";
  assessment: AssessmentResult | null;
  quiz_result: QuizResult | null;
  questions: Question[] | null;
  detail_available: boolean;
}

export interface ActivityItem {
  kind: string;
  title: string;
  detail: string;
  score: number | null;
  timestamp: string;
}

export interface ChapterRef {
  chapter_id: string;
  chapter: string;
  subject: string;
  mastery: number;
  reason: string;
  is_weak: boolean;
}

export interface RemediationStep {
  concept: string;
  chapter: string;
  chapter_id: string | null;
}

export interface WeakArea {
  chapter_id: string;
  chapter: string;
  subject: string;
  mastery: number;
  severity: number;
  blocks: number;
  blocked: string[];
  remediation: { concept: string; steps: RemediationStep[] } | null;
}

export interface RevisionItem {
  concept: string;
  chapter: string;
  chapter_id: string | null;
  subject: string;
  mastery: number;
  reason: string;
}

export interface CompletedItem {
  chapter_id: string;
  chapter: string;
  subject: string;
  score: number;
  timestamp: string;
}

export interface Recommendation {
  kind: "remediation" | "unlock" | "continue" | "advance" | "revise";
  title: string;
  text: string;
  action_label: string;
  action_chapter_id: string | null;
}

export interface Interpretations {
  accuracy: string;
  time: string;
  weak: string;
  radar: string;
}

export type JourneyNodeState = "mastered" | "in_progress" | "revision" | "locked" | "available";

export interface JourneyNodeDetail {
  quiz_attempts: number;
  average_score: number | null;
  lessons_completed: number;
  time_spent_minutes: number;
  common_mistakes: string[];
  recommendation: string;
  weak_concepts: { concept: string; mastery: number }[];
  chapter_attempts: number;
}

export interface JourneyNode {
  id: string;
  type: "chapter" | "revision" | "retest";
  label: string;
  subtitle: string;
  state: JourneyNodeState;
  mastery: number;
  chapter_id: string;
  chapter_name: string;
  subject: string;
  slug: string;
  inserted?: boolean;
  reason?: string;
  detail: JourneyNodeDetail;
}

export interface JourneyEdge {
  from: string;
  to: string;
}

export interface MasteryJourney {
  nodes: JourneyNode[];
  edges: JourneyEdge[];
  focus_node_id: string | null;
  current_subject: string | null;
  current_module: string | null;
  stats: Record<string, number>;
}

export interface Dashboard {
  overall_progress: number;
  jee_readiness: number;
  predicted_jee_score: number;
  subject_score_breakdown?: { physics: number; chemistry: number; maths: number };
  accuracy: number;
  time_spent_hours: number;
  subject_mastery: { subject: string; slug: string; mastery: number }[];
  chapter_mastery: { chapter: string; subject: string; mastery: number }[];
  weak_topics: { chapter: string; subject: string; mastery: number }[];
  strong_topics: { chapter: string; subject: string; mastery: number }[];
  recommended_chapters: ChapterRef[];
  recent_activity: ActivityItem[];
  chapters_completed: number;
  quizzes_attempted: number;
  // V2 command center
  continue_learning: ChapterRef | null;
  next_recommended: ChapterRef[];
  weak_areas: WeakArea[];
  strong_areas: { chapter: string; subject: string; mastery: number }[];
  revision_queue: RevisionItem[];
  recently_completed: CompletedItem[];
  ai_recommendations: Recommendation[];
  interpretations: Interpretations;
  mastery_journey: MasteryJourney;
}

export interface SocratesContextPayload {
  subject?: string;
  chapter?: string;
  section?: string;
  formulas?: string[];
  examples?: string[];
}

export interface Mastery {
  chapter: string;
  subject: string;
  mastery_score: number;
  attempts: number;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  powered_by: string;
  difficulty?: string;
}

export interface ChatTurn {
  id: string;
  role: "user" | "socrates";
  content: string;
  timestamp: string;
  difficulty?: string;
}

export interface ChatSession {
  session_id: string;
  preview: string;
  last_at: string;
  turns: number;
}

export const MIN_QUIZ_QUESTIONS = 4;
