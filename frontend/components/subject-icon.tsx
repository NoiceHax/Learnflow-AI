import { Atom, FlaskConical, Hexagon, Sigma, BookOpen, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

const ICONS: Record<string, LucideIcon> = {
  atom: Atom,
  sigma: Sigma,
  "flask-conical": FlaskConical,
  hexagon: Hexagon,
};

export function SubjectIcon({ icon, className }: { icon: string; className?: string }) {
  const Icon = ICONS[icon] ?? BookOpen;
  return <Icon className={cn("size-4", className)} />;
}
