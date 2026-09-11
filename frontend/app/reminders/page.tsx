"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const REMINDER_TYPE_CONFIG: Record<string, { icon: string; color: string; bg: string }> = {
  INVENTORY: { icon: "📦", color: "text-red-600", bg: "bg-red-50 border-red-100" },
  MONTHLY_GROCERY: { icon: "🛒", color: "text-[#FF9900]", bg: "bg-orange-50 border-orange-100" },
  PRICE_ALERT: { icon: "💰", color: "text-blue-600", bg: "bg-blue-50 border-blue-100" },
  REORDER: { icon: "🔄", color: "text-purple-600", bg: "bg-purple-50 border-purple-100" },
  APPROVAL: { icon: "✋", color: "text-orange-600", bg: "bg-orange-50 border-orange-100" },
  DELIVERY: { icon: "🚚", color: "text-green-600", bg: "bg-green-50 border-green-100" },
};

export default function RemindersPage() {
  const [reminders, setReminders] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"ALL" | "ACTIVE" | "COMPLETED">("ACTIVE");

  const loadReminders = () => {
    const status = filter === "ALL" ? undefined : filter;
    const url = status ? `/api/reminders?status=${status}` : "/api/reminders?status=";
    fetch(url)
      .then(r => r.json())
      .then(data => setReminders(data?.reminders || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { loadReminders(); }, [filter]);

  const handleAction = async (id: string, action: "snooze" | "complete" | "dismiss") => {
    await fetch(`/api/reminders/${id}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action }),
    });
    loadReminders();
  };

  const grouped = reminders.reduce((acc: Record<string, any[]>, rem) => {
    const type = rem.type || "OTHER";
    if (!acc[type]) acc[type] = [];
    acc[type].push(rem);
    return acc;
  }, {});

  const priorityOrder = ["HIGH", "MEDIUM", "LOW"];
  const sortedReminders = [...reminders].sort((a, b) =>
    priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority)
  );

  return (
    <div className="min-h-screen bg-[#FCFBF9]">
      <div className="max-w-3xl mx-auto px-4 md:px-8 py-8">

        {/* Header */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-2">NOVA · Household Intelligence</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Things worth remembering</h1>
          <p className="text-neutral-500">Contextual household reminders — not just calendar alerts.</p>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 mb-6">
          {(["ACTIVE", "ALL", "COMPLETED"] as const).map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-colors ${filter === f ? "bg-neutral-900 text-white" : "bg-white border border-neutral-200 text-neutral-600 hover:border-neutral-400"}`}
            >
              {f === "ACTIVE" ? "Active" : f === "ALL" ? "All" : "Done"}
            </button>
          ))}
          <button
            onClick={loadReminders}
            className="ml-auto px-3 py-2 text-neutral-400 hover:text-neutral-900 transition-colors"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin"></div>
          </div>
        ) : sortedReminders.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-neutral-200">
            <p className="text-4xl mb-4">🎉</p>
            <p className="text-neutral-700 font-semibold">All caught up!</p>
            <p className="text-neutral-400 text-sm mt-1">No reminders in this category.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {sortedReminders.map(rem => {
              const cfg = REMINDER_TYPE_CONFIG[rem.type] || { icon: "•", color: "text-neutral-500", bg: "bg-white border-neutral-200" };
              const isDone = rem.status === "COMPLETED" || rem.status === "DISMISSED";
              return (
                <div key={rem.id} className={`rounded-2xl border p-5 ${cfg.bg} ${isDone ? "opacity-60" : ""} hover:shadow-sm transition-all`}>
                  <div className="flex items-start gap-4">
                    <span className="text-2xl shrink-0">{cfg.icon}</span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <p className="text-sm font-bold text-neutral-900">{rem.title}</p>
                            <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${rem.priority === "HIGH" ? "bg-red-100 text-red-700" : rem.priority === "MEDIUM" ? "bg-yellow-100 text-yellow-700" : "bg-neutral-100 text-neutral-500"}`}>
                              {rem.priority}
                            </span>
                          </div>
                          <p className="text-sm text-neutral-600 mt-1 leading-relaxed">{rem.message}</p>
                        </div>
                      </div>

                      {/* Action link */}
                      {rem.action_url && !isDone && (
                        <Link href={rem.action_url} className={`inline-block mt-2 text-xs font-semibold ${cfg.color} hover:underline`}>
                          Take action →
                        </Link>
                      )}

                      {/* Action buttons */}
                      {!isDone && (
                        <div className="flex gap-2 mt-3">
                          <button
                            onClick={() => handleAction(rem.id, "complete")}
                            className="px-3 py-1.5 bg-green-100 text-green-700 text-xs font-bold rounded-lg hover:bg-green-200 transition-colors"
                          >Done</button>
                          <button
                            onClick={() => handleAction(rem.id, "snooze")}
                            className="px-3 py-1.5 bg-neutral-100 text-neutral-600 text-xs font-bold rounded-lg hover:bg-neutral-200 transition-colors"
                          >Snooze 24h</button>
                          <button
                            onClick={() => handleAction(rem.id, "dismiss")}
                            className="px-3 py-1.5 text-neutral-400 text-xs font-bold rounded-lg hover:text-neutral-600 transition-colors"
                          >Dismiss</button>
                        </div>
                      )}
                      {isDone && (
                        <p className="text-xs text-neutral-400 mt-2">{rem.status === "COMPLETED" ? "✓ Completed" : "Dismissed"}</p>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
