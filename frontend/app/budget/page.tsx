"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function BudgetPage() {
  const [budget, setBudget] = useState<any>(null);
  const [savings, setSavings] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch("/api/budget").then(r => r.json()).catch(() => null),
      fetch("/api/savings").then(r => r.json()).catch(() => null),
    ]).then(([bud, sav]) => {
      setBudget(bud);
      setSavings(sav);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FCFBF9] flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin"></div>
      </div>
    );
  }

  const monthly = budget?.monthly || 5500;
  const spent = budget?.spent || 3940;
  const remaining = budget?.remaining || 1560;
  const autoLimit = budget?.auto_limit || 500;
  const spentPct = Math.min(100, (spent / monthly) * 100);

  const upcoming = [
    { label: "Essential", items: ["Milk (2L)", "Atta 5kg", "Rice 5kg"], estimated: 920 },
    { label: "Expected", items: ["Tea 500g", "Dal 1kg", "Soap"], estimated: 480 },
    { label: "Optional", items: ["Detergent (wait)", "Shampoo"], estimated: 410 },
  ];

  const projectedTotal = spent + 920 + 480;
  const projectedStatus = projectedTotal <= monthly ? "WITHIN" : "OVER";

  return (
    <div className="min-h-screen bg-[#FCFBF9]">
      <div className="max-w-4xl mx-auto px-4 md:px-8 py-8">

        {/* Header */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-2">NOVA · Budget Intelligence</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">September budget</h1>
          <p className="text-neutral-500">NOVA connects your Amazon spending to household planning.</p>
        </div>

        {/* Main budget card */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 md:p-8 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6 mb-6">
            <div>
              <p className="text-sm text-neutral-500 mb-1">Monthly household budget</p>
              <p className="text-5xl font-black text-neutral-900">₹{monthly.toLocaleString("en-IN")}</p>
            </div>
            <div className="flex gap-4">
              <div className="text-center">
                <p className="text-2xl font-black text-neutral-900">₹{spent.toLocaleString("en-IN")}</p>
                <p className="text-xs text-neutral-400 mt-0.5">Spent this month</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-black text-green-700">₹{remaining.toLocaleString("en-IN")}</p>
                <p className="text-xs text-neutral-400 mt-0.5">Available</p>
              </div>
            </div>
          </div>

          {/* Budget bar */}
          <div className="mb-4">
            <div className="w-full h-4 bg-neutral-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${spentPct > 90 ? "bg-red-500" : spentPct > 70 ? "bg-[#FF9900]" : "bg-green-500"}`}
                style={{ width: `${spentPct}%` }}
              ></div>
            </div>
            <div className="flex justify-between mt-1.5">
              <p className="text-xs text-neutral-400">₹0</p>
              <p className={`text-xs font-semibold ${spentPct > 90 ? "text-red-600" : "text-neutral-500"}`}>{spentPct.toFixed(0)}% used</p>
              <p className="text-xs text-neutral-400">₹{monthly.toLocaleString("en-IN")}</p>
            </div>
          </div>

          <div className="flex items-center gap-2 p-3 bg-neutral-50 rounded-xl">
            <div className="w-2 h-2 rounded-full bg-green-500"></div>
            <p className="text-xs text-neutral-600">Auto-buy limit per item: <strong>₹{autoLimit}</strong></p>
          </div>
        </div>

        {/* Upcoming purchases */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-6">
          <h2 className="text-lg font-black text-neutral-900 mb-4">Predicted upcoming Amazon purchases</h2>
          <div className="space-y-3">
            {upcoming.map((u) => (
              <div key={u.label} className={`flex items-start gap-4 p-4 rounded-2xl border ${u.label === "Essential" ? "bg-orange-50 border-orange-100" : u.label === "Expected" ? "bg-blue-50 border-blue-100" : "bg-neutral-50 border-neutral-100"}`}>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold ${u.label === "Essential" ? "text-orange-700" : u.label === "Expected" ? "text-blue-700" : "text-neutral-500"}`}>{u.label}</span>
                  </div>
                  <p className="text-xs text-neutral-500">{u.items.join(" · ")}</p>
                </div>
                <p className="text-base font-black text-neutral-900 shrink-0">₹{u.estimated.toLocaleString("en-IN")}</p>
              </div>
            ))}
          </div>
        </div>

        {/* NOVA forecast */}
        <div className={`rounded-3xl border p-6 mb-6 ${projectedStatus === "WITHIN" ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}>
          <h2 className="text-lg font-black text-neutral-900 mb-4">NOVA forecast</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-neutral-500 mb-1">Spent so far</p>
              <p className="text-xl font-black text-neutral-900">₹{spent.toLocaleString("en-IN")}</p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Expected to add</p>
              <p className="text-xl font-black text-neutral-900">₹{(920 + 480).toLocaleString("en-IN")}</p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Projected month-end</p>
              <p className={`text-xl font-black ${projectedStatus === "WITHIN" ? "text-green-700" : "text-red-600"}`}>₹{projectedTotal.toLocaleString("en-IN")}</p>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            <span className={`text-sm font-bold ${projectedStatus === "WITHIN" ? "text-green-700" : "text-red-700"}`}>
              {projectedStatus === "WITHIN" ? "✓ Within budget" : "⚠ Over budget"}
            </span>
            {projectedStatus === "WITHIN" && (
              <span className="text-sm text-green-600">— ₹{(monthly - projectedTotal).toLocaleString("en-IN")} to spare</span>
            )}
          </div>
        </div>

        {/* Savings */}
        {savings && savings.total_potential_saving > 0 && (
          <div className="bg-white rounded-3xl border border-neutral-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-black text-neutral-900">NOVA found savings</h2>
              <span className="text-2xl font-black text-green-700">₹{savings.total_potential_saving}</span>
            </div>
            <p className="text-sm text-neutral-500 mb-4">{savings.summary}</p>
            <div className="space-y-2">
              {(savings.opportunities || []).map((opp: any) => (
                <div key={opp.id} className="flex items-center gap-3 p-3 bg-green-50 rounded-xl border border-green-100">
                  <span className="text-green-500 text-sm">💚</span>
                  <p className="text-xs text-neutral-700 flex-1">{opp.reason}</p>
                  <span className="text-xs font-bold text-green-700 shrink-0">Save ₹{opp.potential_saving}</span>
                </div>
              ))}
            </div>
            <Link href="/price-watch" className="mt-4 block text-center text-sm font-semibold text-[#FF9900] hover:underline">
              View Price Watch →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
