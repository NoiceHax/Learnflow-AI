"use client";

import { createContext, useCallback, useContext, useState } from "react";
import type { SocratesContextPayload } from "@/lib/types";

interface SocratesState {
  context: SocratesContextPayload | null;
  open: boolean;
  setContext: (c: SocratesContextPayload | null) => void;
  clearContext: () => void;
  setOpen: (b: boolean) => void;
  /** Open the assistant, optionally seeding a question. */
  ask: (prompt?: string) => void;
  pending: string | null;
  consumePending: () => string | null;
}

const Ctx = createContext<SocratesState | null>(null);

export function SocratesProvider({ children }: { children: React.ReactNode }) {
  const [context, setContextState] = useState<SocratesContextPayload | null>(null);
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState<string | null>(null);

  const setContext = useCallback((c: SocratesContextPayload | null) => setContextState(c), []);
  const clearContext = useCallback(() => setContextState(null), []);
  const ask = useCallback((prompt?: string) => {
    if (prompt) setPending(prompt);
    setOpen(true);
  }, []);
  const consumePending = useCallback(() => {
    let p: string | null = null;
    setPending((cur) => {
      p = cur;
      return null;
    });
    return p;
  }, []);

  return (
    <Ctx.Provider value={{ context, open, setContext, clearContext, setOpen, ask, pending, consumePending }}>
      {children}
    </Ctx.Provider>
  );
}

export function useSocrates() {
  const c = useContext(Ctx);
  if (!c) throw new Error("useSocrates must be used within SocratesProvider");
  return c;
}
