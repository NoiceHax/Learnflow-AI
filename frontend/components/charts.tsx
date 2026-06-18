"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";

const PRIMARY = "#8b8cf8";

function masteryFill(v: number) {
  if (v >= 80) return "#4ade80";
  if (v >= 60) return PRIMARY;
  if (v >= 40) return "#fbbf24";
  return "#f87171";
}

export function ChapterRadar({ data }: { data: { chapter: string; mastery: number }[] }) {
  if (data.length < 3) {
    return <EmptyChart message="Complete a few more quizzes to populate the radar." />;
  }
  return (
    <ResponsiveContainer width="100%" height={300}>
      <RadarChart data={data} outerRadius="72%">
        <PolarGrid stroke="hsl(var(--border))" />
        <PolarAngleAxis dataKey="chapter" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
        <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
        <Radar dataKey="mastery" stroke={PRIMARY} fill={PRIMARY} fillOpacity={0.35} />
        <Tooltip
          contentStyle={{
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(v: number) => [`${v}%`, "Mastery"]}
        />
      </RadarChart>
    </ResponsiveContainer>
  );
}

export function MasteryBars({ data }: { data: { label: string; mastery: number }[] }) {
  if (!data.length) return <EmptyChart message="No data yet." />;
  return (
    <ResponsiveContainer width="100%" height={Math.max(180, data.length * 42)}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
        <XAxis type="number" domain={[0, 100]} hide />
        <YAxis
          type="category"
          dataKey="label"
          width={118}
          tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 12 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          cursor={{ fill: "hsl(var(--muted) / 0.4)" }}
          contentStyle={{
            background: "hsl(var(--card))",
            border: "1px solid hsl(var(--border))",
            borderRadius: 8,
            fontSize: 12,
          }}
          formatter={(v: number) => [`${v}%`, "Mastery"]}
        />
        <Bar dataKey="mastery" radius={[0, 6, 6, 0]} barSize={20}>
          {data.map((d, i) => (
            <Cell key={i} fill={masteryFill(d.mastery)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

function EmptyChart({ message }: { message: string }) {
  return (
    <div className="flex h-[200px] items-center justify-center text-center text-sm text-muted-foreground">
      {message}
    </div>
  );
}
