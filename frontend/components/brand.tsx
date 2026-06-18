import { cn } from "@/lib/utils";

/**
 * LEARNFLOW AI wordmark: Hanken Grotesk, the "AI" set in the single indigo accent.
 */
export function Brand({ className, showText = true }: { className?: string; showText?: boolean }) {
  return (
    <span className={cn("brand select-none", className)}>
      LEARNFLOW&nbsp;<b>AI</b>
      {!showText && null}
    </span>
  );
}
