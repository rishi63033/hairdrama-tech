/**
 * StatsBar component
 * Shows quick summary counts: Total, Pending, In Progress, Completed
 */

import { Task } from "@/types";

interface StatsBarProps {
  tasks: Task[];
}

export default function StatsBar({ tasks }: StatsBarProps) {
  const total = tasks.length;
  const pending = tasks.filter((t) => t.status === "pending").length;
  const inProgress = tasks.filter((t) => t.status === "in_progress").length;
  const completed = tasks.filter((t) => t.status === "completed").length;

  const stats = [
    { label: "Total Tasks", value: total, color: "bg-blue-50 text-blue-700 border-blue-100" },
    { label: "Pending", value: pending, color: "bg-yellow-50 text-yellow-700 border-yellow-100" },
    { label: "In Progress", value: inProgress, color: "bg-purple-50 text-purple-700 border-purple-100" },
    { label: "Completed", value: completed, color: "bg-green-50 text-green-700 border-green-100" },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {stats.map((s) => (
        <div
          key={s.label}
          className={`rounded-xl border p-4 ${s.color}`}
        >
          <p className="text-3xl font-bold">{s.value}</p>
          <p className="text-sm mt-1 opacity-80">{s.label}</p>
        </div>
      ))}
    </div>
  );
}
