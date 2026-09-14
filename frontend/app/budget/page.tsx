"use client";

import { useState, useEffect, useCallback } from "react";
import {
  SlidersHorizontal,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Settings2,
} from "lucide-react";
import BudgetModal from "@/components/BudgetModal";

interface BudgetData {
  monthly: number;
  spent: number;
  remaining: number;
  auto_limit: number;
  currency: string;
  spent_pct: number;
  pressure: boolean;
}

interface PantryItem {
  product_id: string;
  name: string;
  category: string;
  days_remaining: number;
  urgency: string;
}

// Estimated per-category replenishment cost (used for forecast)
const REPLENISHMENT_EST: Record<string, number> = {
  Milk: 68, Oil: 749, Rice: 320, Atta: 289, Salt: 25,
  Dal: 142, Tea: 215, Detergent: 399, Sugar: 210,
  Soap: 139, Cleaning: 109, "Hair Care": 199,
};

const DEFAULT_BUDGET: BudgetData = {
  monthly: 5000,
  spent: 3440,
  remaining: 1560,
  auto_limit: 500,
  currency: "INR",
  spent_pct: 69,
  pressure: false,
};

const DEFAULT_PANTRY: PantryItem[] = [
  { product_id: "p_milk", name: "Amul Taaza Milk 1L", category: "Milk", days_remaining: 0.5, urgency: "URGENT" },
  { product_id: "p_detergent", name: "Surf Excel Matic Front Load 2kg", category: "Detergent", days_remaining: 2.8, urgency: "UPCOMING" },
  { product_id: "p_oil", name: "Fortune Sunlite Sunflower Oil 5L", category: "Oil", days_remaining: 30, urgency: "COMFORTABLE" },
];

export default function BudgetPage() {
  const [budget, setBudget] = useState<BudgetData>(DEFAULT_BUDGET);
  const [pantry, setPantry] = useState<PantryItem[]>(DEFAULT_PANTRY);
  const [savings, setSavings] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isBudgetModalOpen, setIsBudgetModalOpen] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const [bud, pant, sav] = await Promise.all([
        fetch("/api/budget").then((r) => r.ok ? r.json() : null).catch(() => null),
        fetch("/api/pantry").then((r) => r.ok ? r.json() : null).catch(() => []),
        fetch("/api/savings").then((r) => r.ok ? r.json() : null).catch(() => null),
      ]);
      if (bud && typeof bud.monthly === "number") setBudget(bud);
      if (Array.isArray(pant) && pant.length > 0) setPantry(pant);
      if (sav) setSavings(sav);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const handleUpdate = () => loadData();
    window.addEventListener("budget-updated", handleUpdate);
    window.addEventListener("household-updated", handleUpdate);
    return () => {
      window.removeEventListener("budget-updated", handleUpdate);
      window.removeEventListener("household-updated", handleUpdate);
    };
  }, [loadData]);

  if (loading || !budget) {
    return (
      <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center pt-20">
        <div className="flex flex-col items-center gap-3">
          <img src="/logo.png" alt="NOVA" className="h-8 w-auto object-contain opacity-80" />
          <div className="w-6 h-6 border-2 border-neutral-300 border-t-neutral-800 rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  // Derive upcoming spend from real pantry state
  const urgentAndUpcoming = pantry.filter(
    (i) => i.urgency === "URGENT" || i.urgency === "UPCOMING"
  );
  const estimatedUpcomingSpend = urgentAndUpcoming.reduce(
    (sum, item) => sum + (REPLENISHMENT_EST[item.category] ?? 120),
    0
  );
  const projectedTotal = budget.spent + estimatedUpcomingSpend;
  const projectedRemaining = budget.monthly - projectedTotal;
  const projectedStatus = projectedTotal <= budget.monthly ? "WITHIN" : "OVER";
  const spentPct = budget.spent_pct ?? Math.min(100, Math.round((budget.spent / budget.monthly) * 100));

  // Build upcoming breakdown from pantry
  const upcomingGroups = [
    {
      label: "Running low",
      items: pantry.filter((i) => i.urgency === "URGENT"),
      color: "bg-red-50 border-red-100",
      textColor: "text-red-700",
    },
    {
      label: "Coming up this week",
      items: pantry.filter((i) => i.urgency === "UPCOMING"),
      color: "bg-amber-50 border-amber-100",
      textColor: "text-amber-700",
    },
  ].filter((g) => g.items.length > 0);

  return (
    <div className="min-h-screen bg-[#FAFAF8] pt-20 pb-32">
      <div className="max-w-2xl mx-auto px-4 md:px-6">

        {/* Header */}
        <div className="pt-8 pb-6">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-1">NOVA · Budget Intelligence</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Budget</h1>
          <p className="text-neutral-500">
            NOVA manages your household spending within these limits.
          </p>
        </div>

        {/* Main budget card */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 md:p-8 mb-5">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-5">
            <div>
              <p className="text-sm text-neutral-500 mb-1">Monthly household budget</p>
              <div className="flex items-center gap-3">
                <p className="text-5xl font-black text-neutral-900">
                  ₹{budget.monthly.toLocaleString("en-IN")}
                </p>
                <button
                  type="button"
                  onClick={() => setIsBudgetModalOpen(true)}
                  className="px-3 py-1.5 rounded-xl bg-amber-100 hover:bg-amber-200 text-amber-900 font-bold text-xs flex items-center gap-1.5 transition-colors"
                >
                  <SlidersHorizontal className="w-3.5 h-3.5 text-[#FF9900]" />
                  Edit
                </button>
              </div>
            </div>
            <div className="flex gap-5">
              <div>
                <p className="text-2xl font-black text-neutral-900">
                  ₹{budget.spent.toLocaleString("en-IN")}
                </p>
                <p className="text-xs text-neutral-400 mt-0.5">Spent this month</p>
              </div>
              <div>
                <p className={`text-2xl font-black ${budget.remaining < 500 ? "text-red-600" : "text-emerald-700"}`}>
                  ₹{budget.remaining.toLocaleString("en-IN")}
                </p>
                <p className="text-xs text-neutral-400 mt-0.5">Available</p>
              </div>
            </div>
          </div>

          {/* Progress bar */}
          <div className="mb-4">
            <div className="w-full h-3 bg-neutral-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  spentPct > 90 ? "bg-red-500" : spentPct > 70 ? "bg-amber-500" : "bg-emerald-500"
                }`}
                style={{ width: `${spentPct}%` }}
              />
            </div>
            <div className="flex justify-between mt-1.5">
              <p className="text-xs text-neutral-400">₹0</p>
              <p className={`text-xs font-semibold ${spentPct > 90 ? "text-red-600" : "text-neutral-500"}`}>
                {spentPct}% used
              </p>
              <p className="text-xs text-neutral-400">₹{budget.monthly.toLocaleString("en-IN")}</p>
            </div>
          </div>

          {/* Auto-limit */}
          <div className="flex items-center justify-between p-3 bg-neutral-50 rounded-xl">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500" />
              <p className="text-xs text-neutral-600">
                Auto-buy limit: <strong>₹{budget.auto_limit}</strong> per item
              </p>
            </div>
            <button
              type="button"
              onClick={() => setIsBudgetModalOpen(true)}
              className="text-xs font-bold text-neutral-500 hover:text-neutral-900 flex items-center gap-1"
            >
              <Settings2 className="w-3.5 h-3.5" /> Adjust
            </button>
          </div>
        </div>

        {/* Upcoming purchases - derived from pantry */}
        {upcomingGroups.length > 0 && (
          <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-5">
            <h2 className="text-base font-black text-neutral-900 mb-4">
              Expected replenishment
            </h2>
            <p className="text-xs text-neutral-400 mb-4">
              Based on your current pantry levels.
            </p>
            <div className="space-y-3">
              {upcomingGroups.map((group) => {
                const groupCost = group.items.reduce(
                  (s, i) => s + (REPLENISHMENT_EST[i.category] ?? 120),
                  0
                );
                return (
                  <div
                    key={group.label}
                    className={`flex items-start gap-4 p-4 rounded-2xl border ${group.color}`}
                  >
                    <div className="flex-1">
                      <span className={`text-xs font-bold ${group.textColor}`}>{group.label}</span>
                      <p className="text-xs text-neutral-500 mt-1">
                        {group.items.map((i) => i.name.split(" ")[0]).join(", ")}
                      </p>
                    </div>
                    <p className="text-base font-black text-neutral-900 shrink-0">
                      ~₹{groupCost.toLocaleString("en-IN")}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* NOVA forecast */}
        <div
          className={`rounded-3xl border p-6 mb-5 ${
            projectedStatus === "WITHIN"
              ? "bg-emerald-50 border-emerald-200"
              : "bg-red-50 border-red-200"
          }`}
        >
          <h2 className="text-base font-black text-neutral-900 mb-4">NOVA forecast</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-xs text-neutral-500 mb-1">Spent so far</p>
              <p className="text-xl font-black text-neutral-900">₹{budget.spent.toLocaleString("en-IN")}</p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Expected to add</p>
              <p className="text-xl font-black text-neutral-900">
                ₹{estimatedUpcomingSpend.toLocaleString("en-IN")}
              </p>
            </div>
            <div>
              <p className="text-xs text-neutral-500 mb-1">Projected end</p>
              <p
                className={`text-xl font-black ${
                  projectedStatus === "WITHIN" ? "text-emerald-700" : "text-red-600"
                }`}
              >
                ₹{projectedTotal.toLocaleString("en-IN")}
              </p>
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            {projectedStatus === "WITHIN" ? (
              <span className="flex items-center gap-1.5 text-sm font-bold text-emerald-700">
                <CheckCircle2 className="w-4 h-4" /> Within budget
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-sm font-bold text-red-700">
                <AlertTriangle className="w-4 h-4" /> Over budget
              </span>
            )}
            {projectedStatus === "WITHIN" ? (
              <span className="text-sm text-emerald-600">
                - ₹{projectedRemaining.toLocaleString("en-IN")} to spare
              </span>
            ) : (
              <span className="text-sm text-red-600">
                - ₹{Math.abs(projectedRemaining).toLocaleString("en-IN")} shortfall
              </span>
            )}
          </div>
        </div>

        {/* Savings */}
        {savings && savings.total_potential_saving > 0 && (
          <div className="bg-white rounded-3xl border border-neutral-200 p-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-black text-neutral-900">NOVA found savings</h2>
              <span className="text-xl font-black text-emerald-700">
                ₹{savings.total_potential_saving}
              </span>
            </div>
            <p className="text-sm text-neutral-500 mb-4">{savings.summary}</p>
            <div className="space-y-2">
              {(savings.opportunities || []).map((opp: any) => (
                <div
                  key={opp.id}
                  className="flex items-center gap-3 p-3 bg-emerald-50 rounded-xl border border-emerald-100"
                >
                  <Sparkles className="w-4 h-4 text-emerald-600 shrink-0" />
                  <p className="text-xs text-neutral-700 flex-1">{opp.reason}</p>
                  <span className="text-xs font-bold text-emerald-700 shrink-0">
                    Save ₹{opp.potential_saving}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <BudgetModal
        isOpen={isBudgetModalOpen}
        onClose={() => {
          setIsBudgetModalOpen(false);
          loadData();
        }}
        initialMonthly={budget.monthly}
        initialAutoLimit={budget.auto_limit}
      />
    </div>
  );
}
