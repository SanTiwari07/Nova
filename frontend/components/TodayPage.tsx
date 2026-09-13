"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Sparkles,
  ChevronRight,
  ShieldCheck,
  Clock,
  AlertCircle,
  CheckCircle2,
  MinusCircle,
  Zap,
  ArrowRight,
  RotateCcw,
  ShoppingCart,
} from "lucide-react";
import CommandBox from "@/components/CommandBox";

// ─── Types ─────────────────────────────────────────────────────────────────
interface PantryItem {
  product_id: string;
  name: string;
  quantity: number;
  unit: string;
  days_remaining: number;
  status: string;
  urgency: string;
  category: string;
  confidence: number;
  confidence_score: string;
  confidence_level: string;
}

interface HouseholdStatus {
  greeting: string;
  headline: string;
  household_size: number;
  autonomy_profile: string;
  autopilot_on: boolean;
  pantry: {
    total_tracked: number;
    urgent_count: number;
    upcoming_count: number;
    comfortable_count: number;
    uncertain_count: number;
    urgent_items: PantryItem[];
    upcoming_items: PantryItem[];
  };
  budget: {
    spent: number;
    remaining: number;
    monthly: number;
    auto_limit: number;
    estimated_upcoming: number;
    projected_total: number;
    projected_remaining: number;
    over_budget: boolean;
  };
  activity: {
    recent: Array<{ id: string; product: string; decision: string; reasons: string[]; timestamp: string }>;
    auto_count: number;
    restraint_count: number;
    ask_count: number;
  };
  cart: { item_count: number };
}

// ─── Decision colour helpers ────────────────────────────────────────────────
const DECISION_CONFIG: Record<string, { label: string; color: string; icon: React.ReactNode; bg: string }> = {
  AUTO: {
    label: "Taken care of",
    color: "text-emerald-700",
    bg: "bg-emerald-50 border-emerald-100",
    icon: <CheckCircle2 className="w-4 h-4 text-emerald-600" />,
  },
  DO_NOTHING: {
    label: "No action needed",
    color: "text-neutral-500",
    bg: "bg-neutral-50 border-neutral-100",
    icon: <MinusCircle className="w-4 h-4 text-neutral-400" />,
  },
  ASK: {
    label: "Needs your input",
    color: "text-amber-700",
    bg: "bg-amber-50 border-amber-100",
    icon: <AlertCircle className="w-4 h-4 text-amber-500" />,
  },
  BLOCKED: {
    label: "Blocked by rules",
    color: "text-red-700",
    bg: "bg-red-50 border-red-100",
    icon: <ShieldCheck className="w-4 h-4 text-red-500" />,
  },
  WAIT: {
    label: "Waiting",
    color: "text-blue-700",
    bg: "bg-blue-50 border-blue-100",
    icon: <Clock className="w-4 h-4 text-blue-500" />,
  },
  BUDGET_UPDATED: {
    label: "Budget updated",
    color: "text-violet-700",
    bg: "bg-violet-50 border-violet-100",
    icon: <Zap className="w-4 h-4 text-violet-500" />,
  },
  PANTRY_UPDATED: {
    label: "Pantry updated",
    color: "text-teal-700",
    bg: "bg-teal-50 border-teal-100",
    icon: <CheckCircle2 className="w-4 h-4 text-teal-600" />,
  },
};

function getDecisionConfig(decision: string) {
  return (
    DECISION_CONFIG[decision] ?? {
      label: decision,
      color: "text-neutral-600",
      bg: "bg-neutral-50 border-neutral-100",
      icon: <Sparkles className="w-4 h-4 text-neutral-400" />,
    }
  );
}

function UrgencyBadge({ days, confidence }: { days: number; confidence: number }) {
  if (days <= 1)
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700 uppercase tracking-wider">
        Today
      </span>
    );
  if (days <= 2)
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-orange-100 text-orange-700 uppercase tracking-wider">
        Tomorrow
      </span>
    );
  return (
    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 uppercase tracking-wider">
      {Math.ceil(days)} days
    </span>
  );
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 85 ? "bg-emerald-500" : pct >= 65 ? "bg-amber-400" : "bg-red-400";
  return (
    <div className="flex items-center gap-1.5">
      <div className="w-16 h-1.5 bg-neutral-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-[10px] font-semibold text-neutral-400">{pct}%</span>
    </div>
  );
}

// ─── Main Component ─────────────────────────────────────────────────────────
export default function TodayPage() {
  const [status, setStatus] = useState<HouseholdStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionItem, setActionItem] = useState<string | null>(null);
  const [isActing, setIsActing] = useState(false);

  const loadStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/household-status");
      const data = await res.json();
      setStatus(data);
    } catch {
      // keep previous state
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStatus();
    const refresh = () => loadStatus();
    window.addEventListener("household-updated", refresh);
    window.addEventListener("budget-updated", refresh);
    window.addEventListener("cart-updated", refresh);
    return () => {
      window.removeEventListener("household-updated", refresh);
      window.removeEventListener("budget-updated", refresh);
      window.removeEventListener("cart-updated", refresh);
    };
  }, [loadStatus]);

  const handleTakeCareOf = async (item: PantryItem) => {
    setActionItem(item.product_id);
    setIsActing(true);
    try {
      const prompt = `Take care of ${item.name} — it's running low (${item.quantity} ${item.unit} left, ~${item.days_remaining} days remaining).`;
      await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: prompt }),
      });
      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("cart-updated"));
      await loadStatus();
    } finally {
      setIsActing(false);
      setActionItem(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center pt-20">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-neutral-200 border-t-neutral-800 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-neutral-400 font-medium">NOVA is checking your household…</p>
        </div>
      </div>
    );
  }

  const s = status!;
  const budget = s?.budget;
  const pantry = s?.pantry;
  const activity = s?.activity;

  const spentPct = budget
    ? Math.min(100, Math.round((budget.spent / budget.monthly) * 100))
    : 0;

  return (
    <div className="min-h-screen bg-[#FAFAF8] pt-20 pb-32">
      <div className="max-w-2xl mx-auto px-4 md:px-6">

        {/* ── Greeting ─────────────────────────────────────────────── */}
        <div className="pt-8 pb-6">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-1">NOVA Household Intelligence</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight leading-tight mb-2">
            {s.greeting}.
          </h1>
          <p className="text-neutral-500 text-base">{s.headline}</p>
        </div>

        {/* ── NOVA Summary Band ────────────────────────────────────── */}
        {(activity.auto_count > 0 || activity.restraint_count > 0) && (
          <div className="bg-neutral-900 text-white rounded-2xl p-5 mb-5 flex items-start gap-4">
            <div className="w-8 h-8 rounded-xl bg-[#FF9900]/20 flex items-center justify-center shrink-0">
              <Sparkles className="w-4 h-4 text-[#FF9900]" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-bold mb-1">What NOVA has been up to</p>
              <div className="flex flex-wrap gap-3 text-sm text-neutral-300">
                {activity.auto_count > 0 && (
                  <span className="flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    {activity.auto_count} taken care of
                  </span>
                )}
                {activity.restraint_count > 0 && (
                  <span className="flex items-center gap-1">
                    <MinusCircle className="w-3.5 h-3.5 text-neutral-400" />
                    {activity.restraint_count} left alone
                  </span>
                )}
                {activity.ask_count > 0 && (
                  <span className="flex items-center gap-1 text-amber-300">
                    <AlertCircle className="w-3.5 h-3.5" />
                    {activity.ask_count} need your input
                  </span>
                )}
              </div>
            </div>
            <Link href="/orders" className="text-xs text-neutral-400 hover:text-white flex items-center gap-1 shrink-0">
              See all <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        )}

        {/* ── Needs Your Attention ──────────────────────────────────── */}
        {pantry.urgent_count > 0 && (
          <section className="mb-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-bold tracking-widest text-red-600 uppercase">
                Needs attention · {pantry.urgent_count}
              </h2>
              <Link href="/pantry" className="text-xs text-neutral-400 hover:text-neutral-700">
                See pantry →
              </Link>
            </div>
            <div className="space-y-2">
              {pantry.urgent_items.map((item) => (
                <div
                  key={item.product_id}
                  className="bg-white rounded-2xl border border-red-100 p-4 flex items-center gap-4 hover:border-red-200 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-bold text-neutral-900 text-sm truncate">{item.name}</p>
                      <UrgencyBadge days={item.days_remaining} confidence={item.confidence} />
                    </div>
                    <div className="flex items-center gap-3">
                      <p className="text-xs text-neutral-500">
                        {item.quantity} {item.unit} · ~{item.days_remaining}d left
                      </p>
                      <ConfidenceBar value={item.confidence} />
                    </div>
                  </div>
                  <button
                    onClick={() => handleTakeCareOf(item)}
                    disabled={isActing && actionItem === item.product_id}
                    className="shrink-0 px-3.5 py-2 rounded-xl bg-neutral-900 hover:bg-neutral-800 text-white text-xs font-bold transition-all disabled:opacity-60 flex items-center gap-1.5"
                  >
                    {isActing && actionItem === item.product_id ? (
                      <>
                        <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                        Working…
                      </>
                    ) : (
                      <>
                        <Zap className="w-3.5 h-3.5" />
                        Take care of it
                      </>
                    )}
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Coming Up ────────────────────────────────────────────── */}
        {pantry.upcoming_count > 0 && (
          <section className="mb-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
                Coming up · {pantry.upcoming_count}
              </h2>
            </div>
            <div className="bg-white rounded-2xl border border-neutral-200 divide-y divide-neutral-100 overflow-hidden">
              {pantry.upcoming_items.map((item) => (
                <div key={item.product_id} className="px-4 py-3 flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-amber-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-neutral-800 truncate">{item.name}</p>
                    <p className="text-xs text-neutral-400">
                      {item.quantity} {item.unit} · {item.days_remaining} days
                    </p>
                  </div>
                  <ConfidenceBar value={item.confidence} />
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── All Stocked Empty State ───────────────────────────────── */}
        {pantry.urgent_count === 0 && pantry.upcoming_count === 0 && (
          <div className="bg-white rounded-2xl border border-neutral-200 p-6 mb-5 text-center">
            <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
            <p className="font-bold text-neutral-900 mb-1">Your household is in good shape.</p>
            <p className="text-sm text-neutral-500">
              NOVA is staying out of the way. {pantry.comfortable_count} essentials are well stocked.
            </p>
          </div>
        )}

        {/* ── Budget Snapshot ───────────────────────────────────────── */}
        {budget && (
          <section className="mb-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">Budget</h2>
              <Link href="/budget" className="text-xs text-neutral-400 hover:text-neutral-700">
                Manage →
              </Link>
            </div>
            <div className="bg-white rounded-2xl border border-neutral-200 p-5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-xs text-neutral-400 mb-0.5">Remaining this month</p>
                  <p className={`text-2xl font-black ${budget.remaining < 500 ? "text-red-600" : "text-neutral-900"}`}>
                    ₹{budget.remaining.toLocaleString("en-IN")}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-neutral-400 mb-0.5">of ₹{budget.monthly.toLocaleString("en-IN")}</p>
                  <p className="text-sm font-bold text-neutral-600">
                    ₹{budget.spent.toLocaleString("en-IN")} spent
                  </p>
                </div>
              </div>
              <div className="w-full h-2 bg-neutral-100 rounded-full overflow-hidden mb-2">
                <div
                  className={`h-full rounded-full transition-all duration-700 ${
                    spentPct > 90 ? "bg-red-500" : spentPct > 75 ? "bg-amber-500" : "bg-emerald-500"
                  }`}
                  style={{ width: `${spentPct}%` }}
                />
              </div>
              {budget.over_budget ? (
                <p className="text-xs text-red-600 font-semibold flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5" />
                  Projected spend (₹{budget.projected_total.toLocaleString("en-IN")}) exceeds your monthly limit.
                </p>
              ) : (
                <p className="text-xs text-neutral-400">
                  Auto-purchase limit: ₹{budget.auto_limit} per item ·{" "}
                  {s.autopilot_on ? (
                    <span className="text-emerald-600 font-semibold">Autopilot ON</span>
                  ) : (
                    <span className="text-amber-600 font-semibold">Autopilot OFF</span>
                  )}
                </p>
              )}
            </div>
          </section>
        )}

        {/* ── Recent Activity ───────────────────────────────────────── */}
        {activity.recent.length > 0 && (
          <section className="mb-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">Recent activity</h2>
              <Link href="/orders" className="text-xs text-neutral-400 hover:text-neutral-700">
                All orders →
              </Link>
            </div>
            <div className="bg-white rounded-2xl border border-neutral-200 divide-y divide-neutral-100 overflow-hidden">
              {activity.recent.slice(0, 5).map((evt) => {
                const cfg = getDecisionConfig(evt.decision);
                return (
                  <div key={evt.id} className={`px-4 py-3.5 flex items-start gap-3 ${cfg.bg} border-l-2 border-l-current`}>
                    <span className="mt-0.5">{cfg.icon}</span>
                    <div className="flex-1 min-w-0">
                      <p className={`text-xs font-bold ${cfg.color} uppercase tracking-wide mb-0.5`}>{cfg.label}</p>
                      <p className="text-sm text-neutral-800 font-medium truncate">{evt.product}</p>
                      {evt.reasons[0] && (
                        <p className="text-xs text-neutral-500 mt-0.5 line-clamp-1">{evt.reasons[0]}</p>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* ── Household Quick Stats ─────────────────────────────────── */}
        <div className="grid grid-cols-3 gap-3 mb-8">
          {[
            { label: "Tracking", value: `${pantry.total_tracked} items`, icon: <ShieldCheck className="w-4 h-4 text-neutral-500" /> },
            {
              label: "Household",
              value: `${s.household_size} people`,
              icon: <Sparkles className="w-4 h-4 text-neutral-500" />,
            },
            {
              label: s.autopilot_on ? "Autopilot ON" : "Autopilot OFF",
              value: s.autopilot_on ? "Active" : "Paused",
              icon: <Zap className={`w-4 h-4 ${s.autopilot_on ? "text-emerald-500" : "text-neutral-400"}`} />,
            },
          ].map((stat) => (
            <div key={stat.label} className="bg-white rounded-2xl border border-neutral-200 p-4">
              <div className="mb-2">{stat.icon}</div>
              <p className="text-xs font-semibold text-neutral-900">{stat.value}</p>
              <p className="text-[10px] text-neutral-400 mt-0.5">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* ── Command Box ───────────────────────────────────────────── */}
        <section>
          <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-3">Talk to NOVA</h2>
          <CommandBox
            id="today-command-box"
            onScenarioDispatched={() => {
              setTimeout(() => loadStatus(), 2000);
            }}
          />
        </section>

      </div>
    </div>
  );
}
