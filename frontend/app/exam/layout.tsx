import { ExamShell } from "@/components/exam-shell";

export const metadata = { title: "Astra | Exam Mode" };

export default function ExamLayout({ children }: { children: React.ReactNode }) {
  return <ExamShell>{children}</ExamShell>;
}
