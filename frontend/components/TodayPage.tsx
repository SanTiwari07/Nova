"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Clock,
  MinusCircle,
  ShieldCheck,
  ChevronRight,
  ArrowRight,
  RotateCcw,
  Package,
  Wallet,
  ShoppingBag,
  Info,
  X,
  UtensilsCrossed,
  Layers,
  Check,
  Zap,
} from "lucide-react";
import CommandBox from "@/components/CommandBox";

// ─── Interfaces ──────────────────────────────────────────────────────────────
interface TakenCareItem {
  id: string;
  product: string;
  package_name?: string;
  cost: number;
  summary: string;
  description: string;
  reasons: string[];
  decision: string;
  status_label: string;
  timestamp?: string;
  system_telemetry?: Record<string, any>;
}

interface NeedsInputOption {
  name: string;
  price: number;
  tag?: string;
}

interface NeedsInputItem {
  id: string;
  product: string;
  category?: string;
  days_remaining: number;
  summary: string;
  description: string;
  reasons?: string[];
  options: NeedsInputOption[];
}

interface TonightPlanComponent {
  name?: string;
  item?: string;
  stock?: string;
  status?: string;
  needed?: string;
  price?: number;
}

interface TonightPlan {
  plan_id: string;
  title: string;
  meal: string;
  tagline?: string;
  have_items: TonightPlanComponent[];
  need_items: TonightPlanComponent[];
  estimated_cost: number;
  action_label?: string;
  system_telemetry?: Record<string, any>;
}

interface AllSortedItem {
  id: string;
  product: string;
  days_remaining: number;
  quantity?: string;
  summary: string;
  description: string;
  reasons: string[];
  system_telemetry?: Record<string, any>;
}

interface HouseholdStatusData {
  greeting: string;
  headline: string;
  briefing_summary: {
    title: string;
    bullets: string[];
    taken_count: number;
    input_count: number;
    plan_count: number;
  };
  taken_care_of: TakenCareItem[];
  needs_input: NeedsInputItem[];
  tonight_plan: TonightPlan;
  all_sorted: AllSortedItem[];
  household_size: number;
  autonomy_profile: string;
  autopilot_on: boolean;
  pantry: {
    total_tracked: number;
    urgent_count: number;
    upcoming_count: number;
    comfortable_count: number;
    uncertain_count: number;
  };
  budget: {
    spent: number;
    remaining: number;
    monthly: number;
    auto_limit: number;
  };
  activity: {
    recent: any[];
    auto_count: number;
    restraint_count: number;
    ask_count: number;
  };
  cart: {
    item_count: number;
  };
}

export default function TodayPage() {
  const [status, setStatus] = useState<HouseholdStatusData | null>(null);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [whyModalItem, setWhyModalItem] = useState<TakenCareItem | null>(null);
  const [reviewModalItem, setReviewModalItem] = useState<NeedsInputItem | null>(null);
  const [selectedOption, setSelectedOption] = useState<NeedsInputOption | null>(null);

  // Action states
  const [planActionLoading, setPlanActionLoading] = useState(false);
  const [planActionDone, setPlanActionDone] = useState(false);
  const [optionActionLoading, setOptionActionLoading] = useState(false);

  const loadStatus = useCallback(async () => {
    try {
      const res = await fetch("/api/household-status");
      const data = await res.json();
      setStatus(data);
    } catch {
      // keep existing state on fail
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

  // Handle 1-click plan fulfillment
  const handleTakeCareOfPlan = async () => {
    setPlanActionLoading(true);
    try {
      await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: "Take care of tonight's Maggi plan - order required noodles" }),
      });
      setPlanActionDone(true);
      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("cart-updated"));
      window.dispatchEvent(new Event("budget-updated"));
      setTimeout(() => {
        loadStatus();
      }, 1200);
    } finally {
      setPlanActionLoading(false);
    }
  };

  // Handle selecting an option from Needs Your Input modal
  const handleSelectOptionConfirm = async () => {
    if (!selectedOption || !reviewModalItem) return;
    setOptionActionLoading(true);
    try {
      await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text: `Order ${selectedOption.name} for ${reviewModalItem.product}`,
        }),
      });
      setReviewModalItem(null);
      setSelectedOption(null);
      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("cart-updated"));
      window.dispatchEvent(new Event("budget-updated"));
      await loadStatus();
    } finally {
      setOptionActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center pt-24 pb-20">
        <div className="text-center">
          <div className="w-10 h-10 border-3 border-neutral-300 border-t-neutral-900 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-sm text-neutral-500 font-medium">NOVA is reviewing your household…</p>
        </div>
      </div>
    );
  }

  const s = status!;
  const briefing = s.briefing_summary || {
    title: "NOVA has 3 things for you.",
    bullets: [
      "1 thing is already taken care of.",
      "1 thing may need your attention.",
      "1 plan is ready for tonight.",
    ],
  };

  return (
    <div className="min-h-screen bg-[#FAFAF8] text-neutral-900 pt-6 pb-28">
      <div className="max-w-2xl mx-auto px-4 sm:px-6">

        {/* ── Header: Greeting & Household Briefing Intro ───────────── */}
        <div className="pt-6 pb-6">
          <h1 className="text-3xl sm:text-4xl font-black text-neutral-950 tracking-tight leading-tight mb-1.5">
            {s.greeting}.
          </h1>
          <p className="text-neutral-500 text-base font-normal">
            {s.headline || "Here's what's happening at home."}
          </p>
        </div>

        {/* ── SECTION 1 - NOVA'S BRIEFING SUMMARY ───────────────────── */}
        <section className="mb-8">
          <div className="bg-white rounded-3xl border border-neutral-200/90 p-5 sm:p-6 shadow-xs">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
                Household Briefing
              </p>
            </div>
            
            <h2 className="text-lg sm:text-xl font-bold text-neutral-900 mb-3">
              {briefing.title}
            </h2>

            <div className="space-y-2 text-sm text-neutral-600">
              {briefing.bullets.map((bullet, idx) => (
                <div key={idx} className="flex items-center gap-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-neutral-300 shrink-0" />
                  <span>{bullet}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── SECTION 2 - TAKEN CARE OF (AUTO) ───────────────────────── */}
        {s.taken_care_of && s.taken_care_of.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center justify-between mb-3 px-1">
              <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
                Taken care of
              </h2>
              <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
                Autopilot active
              </span>
            </div>

            <div className="space-y-3">
              {s.taken_care_of.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-3xl border border-emerald-100/90 p-5 sm:p-6 shadow-xs hover:border-emerald-200 transition-all"
                >
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <div>
                      <h3 className="text-lg font-bold text-neutral-950">
                        {item.product}
                      </h3>
                      <p className="text-sm text-neutral-600 mt-1 leading-relaxed">
                        {item.summary}
                      </p>
                    </div>

                    <div className="text-right shrink-0">
                      <p className="text-lg font-extrabold text-neutral-950">
                        ₹{item.cost}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-4 pt-3.5 border-t border-neutral-100 text-xs">
                    <div className="flex items-center gap-1.5 font-bold text-emerald-700">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      <span>Done for you</span>
                    </div>

                    <button
                      type="button"
                      onClick={() => setWhyModalItem(item)}
                      className="text-neutral-500 hover:text-neutral-900 font-semibold underline underline-offset-4 cursor-pointer transition-colors"
                    >
                      Why?
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── SECTION 3 - NEEDS YOUR INPUT (ASK) ────────────────────── */}
        {s.needs_input && s.needs_input.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center justify-between mb-3 px-1">
              <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
                Needs your input
              </h2>
            </div>

            <div className="space-y-3">
              {s.needs_input.map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-3xl border border-amber-200/90 p-5 sm:p-6 shadow-xs hover:border-amber-300 transition-all"
                >
                  <div className="flex items-start justify-between gap-4 mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-lg font-bold text-neutral-950">
                          {item.product}
                        </h3>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-100 text-amber-800 uppercase tracking-wide">
                          ~{item.days_remaining} days left
                        </span>
                      </div>
                      <p className="text-sm text-neutral-600 leading-relaxed">
                        {item.summary}
                      </p>
                      <p className="text-xs text-neutral-500 mt-1">
                        NOVA found {item.options?.length || 3} suitable options for your household.
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-end mt-4 pt-3.5 border-t border-neutral-100">
                    <button
                      type="button"
                      onClick={() => {
                        setReviewModalItem(item);
                        setSelectedOption(item.options[0] || null);
                      }}
                      className="px-4 py-2 rounded-xl bg-neutral-950 hover:bg-neutral-800 text-white text-xs font-bold transition-all shadow-xs cursor-pointer flex items-center gap-1.5"
                    >
                      <span>Review options</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── SECTION 4 - TONIGHT / UPCOMING (PLANS) ─────────────────── */}
        {s.tonight_plan && (
          <section className="mb-8">
            <div className="flex items-center justify-between mb-3 px-1">
              <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
                Tonight
              </h2>
              <Link href="/plans" className="text-xs font-semibold text-neutral-500 hover:text-neutral-900 flex items-center gap-1">
                All plans <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="bg-white rounded-3xl border border-neutral-200/90 p-5 sm:p-6 shadow-xs">
              <div className="flex items-start justify-between gap-4 mb-4">
                <div>
                  <div className="flex items-center gap-1.5 text-xs font-bold text-amber-600 mb-1">
                    <UtensilsCrossed className="w-3.5 h-3.5" />
                    <span>Meal Intent</span>
                  </div>
                  <h3 className="text-xl font-bold text-neutral-950">
                    {s.tonight_plan.title}
                  </h3>
                </div>
                <div className="text-right">
                  <span className="text-xs font-bold text-neutral-400">Estimated</span>
                  <p className="text-lg font-extrabold text-neutral-950">
                    ₹{s.tonight_plan.estimated_cost}
                  </p>
                </div>
              </div>

              {/* In Pantry Breakdown */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-4 p-4 rounded-2xl bg-[#F9F9F8] border border-neutral-100 text-xs">
                <div>
                  <p className="font-bold text-neutral-800 mb-2">You already have:</p>
                  <div className="space-y-1.5">
                    {s.tonight_plan.have_items.map((item, i) => (
                      <div key={i} className="flex items-center gap-2 text-neutral-700">
                        <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 stroke-[3]" />
                        <span className="font-medium">{item.name || item.item}</span>
                        {item.stock && (
                          <span className="text-neutral-400 text-[11px]">({item.stock})</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="font-bold text-neutral-800 mb-2">You need:</p>
                  <div className="space-y-1.5">
                    {s.tonight_plan.need_items.map((item, i) => (
                      <div key={i} className="flex items-center gap-2 text-neutral-900 font-semibold">
                        <div className="w-3.5 h-3.5 rounded-full border-2 border-amber-500 shrink-0" />
                        <span>{item.name || item.item}</span>
                        {item.price && (
                          <span className="text-neutral-500 font-normal text-[11px]">(₹{item.price})</span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Action Button */}
              <div className="flex items-center justify-between mt-4 pt-3 border-t border-neutral-100">
                <span className="text-xs text-neutral-500">
                  {planActionDone ? "Order prepared with missing item." : "1 missing item needed."}
                </span>

                <button
                  type="button"
                  onClick={handleTakeCareOfPlan}
                  disabled={planActionLoading || planActionDone}
                  className={`px-4 py-2.5 rounded-xl text-xs font-bold transition-all flex items-center gap-2 shadow-xs cursor-pointer ${
                    planActionDone
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-neutral-950 hover:bg-neutral-800 text-white"
                  }`}
                >
                  {planActionLoading ? (
                    <>
                      <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                      <span>Reconciling…</span>
                    </>
                  ) : planActionDone ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Taken care of!</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-3.5 h-3.5 text-amber-400" />
                      <span>{s.tonight_plan.action_label || "Take care of it"}</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </section>
        )}

        {/* ── SECTION 5 - HOUSEHOLD STATUS ──────────────────────────── */}
        <section className="mb-8">
          <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-3 px-1">
            Your household
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {/* Pantry shortcut */}
            <Link
              href="/pantry"
              className="bg-white rounded-2xl border border-neutral-200/90 p-4 hover:border-neutral-400 hover:shadow-xs transition-all group block"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-neutral-500 group-hover:text-neutral-900 transition-colors">
                  Pantry
                </span>
                <Package className="w-4 h-4 text-neutral-400 group-hover:text-amber-500 transition-colors" />
              </div>
              <p className="text-lg font-extrabold text-neutral-950">
                {s.pantry.total_tracked} items
              </p>
              <p className="text-xs text-neutral-500 mt-0.5">
                {s.pantry.urgent_count > 0 ? (
                  <span className="text-red-600 font-semibold">{s.pantry.urgent_count} running low</span>
                ) : (
                  <span className="text-emerald-600 font-semibold">All healthy</span>
                )}
              </p>
            </Link>

            {/* Budget shortcut */}
            <Link
              href="/budget"
              className="bg-white rounded-2xl border border-neutral-200/90 p-4 hover:border-neutral-400 hover:shadow-xs transition-all group block"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-neutral-500 group-hover:text-neutral-900 transition-colors">
                  Budget
                </span>
                <Wallet className="w-4 h-4 text-neutral-400 group-hover:text-emerald-500 transition-colors" />
              </div>
              <p className="text-lg font-extrabold text-neutral-950">
                ₹{s.budget.remaining?.toLocaleString("en-IN")}
              </p>
              <p className="text-xs text-neutral-500 mt-0.5">
                of ₹{s.budget.monthly?.toLocaleString("en-IN")} monthly
              </p>
            </Link>

            {/* Orders shortcut */}
            <Link
              href="/orders"
              className="bg-white rounded-2xl border border-neutral-200/90 p-4 hover:border-neutral-400 hover:shadow-xs transition-all group block"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-neutral-500 group-hover:text-neutral-900 transition-colors">
                  Orders
                </span>
                <ShoppingBag className="w-4 h-4 text-neutral-400 group-hover:text-blue-500 transition-colors" />
              </div>
              <p className="text-lg font-extrabold text-neutral-950">
                {s.activity.auto_count || 1} active
              </p>
              <p className="text-xs text-emerald-600 font-semibold mt-0.5">
                1 arriving today
              </p>
            </Link>
          </div>
        </section>

        {/* ── SECTION 6 - ALL SORTED (RESTRAINT DEMONSTRATION) ─────────── */}
        {s.all_sorted && s.all_sorted.length > 0 && (
          <section className="mb-8">
            <div className="flex items-center justify-between mb-3 px-1">
              <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
                All sorted
              </h2>
              <span className="text-xs text-neutral-400 font-medium">Restraint applied</span>
            </div>

            <div className="space-y-3">
              {s.all_sorted.slice(0, 2).map((item) => (
                <div
                  key={item.id}
                  className="bg-white rounded-3xl border border-neutral-200/80 p-5 sm:p-6 shadow-2xs"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-base font-bold text-neutral-900">
                          {item.product}
                        </h3>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-neutral-100 text-neutral-600 uppercase">
                          Safe
                        </span>
                      </div>
                      <p className="text-sm text-neutral-600">
                        {item.summary}
                      </p>
                    </div>
                    <div className="flex items-center gap-1 text-xs font-bold text-neutral-500 shrink-0">
                      <MinusCircle className="w-4 h-4 text-neutral-400" />
                      <span>No action needed</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── SECTION 7 - WHAT CAN I TAKE CARE OF? (NATURAL INPUT) ───── */}
        <section className="mb-12">
          <CommandBox
            id="today-command-box"
            onScenarioDispatched={() => {
              setTimeout(() => loadStatus(), 1500);
            }}
          />
        </section>

      </div>

      {/* ── MODAL: WHY EXPLANATION (Consumer translation of AUTO) ───── */}
      {whyModalItem && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-7 shadow-2xl border border-neutral-200 relative animate-in fade-in zoom-in-95 duration-150">
            <button
              type="button"
              onClick={() => setWhyModalItem(null)}
              className="absolute top-5 right-5 p-2 rounded-full text-neutral-400 hover:text-neutral-800 hover:bg-neutral-100 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 text-xs font-bold text-emerald-700 mb-2">
              <CheckCircle2 className="w-4 h-4" />
              <span>Autopilot Decision Rationale</span>
            </div>

            <h3 className="text-xl font-bold text-neutral-950 mb-1">
              Why NOVA ordered {whyModalItem.product}
            </h3>
            <p className="text-xs text-neutral-500 mb-4">
              Decision verified against pantry inventory, velocity, safety limits, and budget.
            </p>

            <div className="space-y-2.5 mb-6">
              {whyModalItem.reasons.map((r, i) => (
                <div key={i} className="flex items-start gap-2.5 text-xs text-neutral-700 bg-neutral-50 p-3 rounded-xl border border-neutral-100">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                  <span className="leading-relaxed">{r}</span>
                </div>
              ))}
            </div>

            <div className="p-3.5 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center justify-between text-xs text-emerald-900 font-medium mb-6">
              <span>Cost: ₹{whyModalItem.cost}</span>
              <span>Status: Placed via Swiggy Instamart</span>
            </div>

            {/* Collapsible System Telemetry for Hackathon Judges */}
            {whyModalItem.system_telemetry && (
              <div className="pt-3 border-t border-neutral-100">
                <p className="text-[10px] font-mono text-neutral-400 mb-1 flex items-center gap-1">
                  <Layers className="w-3 h-3 text-neutral-400" />
                  <span>Strands Agent Verification</span>
                </p>
                <div className="text-[11px] font-mono text-neutral-600 bg-neutral-100/80 p-2.5 rounded-lg">
                  Verdict: {whyModalItem.system_telemetry.verdict} · Provider: {whyModalItem.system_telemetry.provider}
                </div>
              </div>
            )}

            <div className="mt-5 flex justify-end">
              <button
                type="button"
                onClick={() => setWhyModalItem(null)}
                className="px-5 py-2.5 rounded-xl bg-neutral-950 hover:bg-neutral-800 text-white text-xs font-bold transition-colors cursor-pointer"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── MODAL: REVIEW OPTIONS (Consumer translation of ASK) ──────── */}
      {reviewModalItem && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 sm:p-7 shadow-2xl border border-neutral-200 relative animate-in fade-in zoom-in-95 duration-150">
            <button
              type="button"
              onClick={() => {
                setReviewModalItem(null);
                setSelectedOption(null);
              }}
              className="absolute top-5 right-5 p-2 rounded-full text-neutral-400 hover:text-neutral-800 hover:bg-neutral-100 transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center gap-2 text-xs font-bold text-amber-700 mb-2">
              <AlertCircle className="w-4 h-4" />
              <span>Restock Options Review</span>
            </div>

            <h3 className="text-xl font-bold text-neutral-950 mb-1">
              Select {reviewModalItem.product} option
            </h3>
            <p className="text-xs text-neutral-500 mb-5">
              Choose your preferred pack. NOVA will take care of the rest within your monthly budget.
            </p>

            <div className="space-y-2.5 mb-6">
              {reviewModalItem.options.map((opt, i) => {
                const isSelected = selectedOption?.name === opt.name;
                return (
                  <div
                    key={i}
                    onClick={() => setSelectedOption(opt)}
                    className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between ${
                      isSelected
                        ? "border-neutral-900 bg-neutral-50 ring-1 ring-neutral-900 shadow-xs"
                        : "border-neutral-200 hover:border-neutral-300 bg-white"
                    }`}
                  >
                    <div>
                      <p className="text-xs font-bold text-neutral-900">{opt.name}</p>
                      {opt.tag && (
                        <p className="text-[10px] text-amber-700 font-semibold mt-0.5">{opt.tag}</p>
                      )}
                    </div>
                    <div className="text-right pl-3">
                      <p className="text-sm font-extrabold text-neutral-950">₹{opt.price}</p>
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-neutral-100">
              <button
                type="button"
                onClick={() => {
                  setReviewModalItem(null);
                  setSelectedOption(null);
                }}
                className="px-4 py-2.5 rounded-xl border border-neutral-300 text-neutral-700 hover:bg-neutral-50 text-xs font-semibold cursor-pointer"
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={handleSelectOptionConfirm}
                disabled={!selectedOption || optionActionLoading}
                className="px-5 py-2.5 rounded-xl bg-neutral-950 hover:bg-neutral-800 disabled:opacity-50 text-white text-xs font-bold transition-all shadow-xs cursor-pointer flex items-center gap-1.5"
              >
                {optionActionLoading ? (
                  <>
                    <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                    <span>Ordering…</span>
                  </>
                ) : (
                  <>
                    <span>Confirm &amp; Order</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
