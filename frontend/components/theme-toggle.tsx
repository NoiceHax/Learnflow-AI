"use client";

import { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

export function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  useEffect(() => {
    const isLight = document.documentElement.classList.contains("light");
    setTheme(isLight ? "light" : "dark");
  }, []);

  const toggleTheme = () => {
    const nextTheme = theme === "light" ? "dark" : "light";
    setTheme(nextTheme);

    // Apply temporary transitioning class to HTML to make transitions smooth
    document.documentElement.classList.add("theme-transitioning");

    if (nextTheme === "light") {
      document.documentElement.classList.add("light");
      document.documentElement.classList.remove("dark");
      localStorage.theme = "light";
    } else {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
      localStorage.theme = "dark";
    }

    // Clean up class after animation duration
    setTimeout(() => {
      document.documentElement.classList.remove("theme-transitioning");
    }, 450);
  };

  return (
    <button
      onClick={toggleTheme}
      className="navlink theme-toggle-btn"
      aria-label="Toggle theme"
      style={{
        width: 36,
        height: 36,
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        borderRadius: "var(--radius-md)",
        border: "1px solid var(--hairline)",
        background: "var(--surface-2)",
        color: "var(--text)",
        cursor: "pointer",
        padding: 0,
        position: "relative",
        overflow: "hidden",
      }}
    >
      <div style={{ position: "relative", width: 18, height: 18, display: "flex", alignItems: "center", justifyContent: "center" }}>
        {/* Sun icon */}
        <Sun
          size={18}
          style={{
            position: "absolute",
            transition: "transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.4s ease",
            opacity: theme === "light" ? 1 : 0,
            transform: theme === "light" ? "rotate(0deg) scale(1)" : "rotate(-90deg) scale(0)",
            color: "var(--indigo)",
          }}
        />
        {/* Moon icon */}
        <Moon
          size={18}
          style={{
            position: "absolute",
            transition: "transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.4s ease",
            opacity: theme === "dark" ? 1 : 0,
            transform: theme === "dark" ? "rotate(0deg) scale(1)" : "rotate(90deg) scale(0)",
            color: "var(--indigo-bright)",
          }}
        />
      </div>
    </button>
  );
}
