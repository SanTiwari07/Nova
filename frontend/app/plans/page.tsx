"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import ProductImage from "@/components/ProductImage";
import {
  UtensilsCrossed,
  Check,
  ShoppingBag,
  Sparkles,
  RotateCcw,
  CheckCircle2,
  Clock,
  ChevronRight,
  ArrowRight,
  Zap,
} from "lucide-react";

interface PlanItem {
  plan_id: string;
  key: string;
  title: string;
  meal: string;
  have_items: Array<{ item: string; stock: string; status: string; imageUrl?: string }>;
  need_items: Array<{ item: string; needed: string; estimated_price: number; imageUrl?: string }>;
  ready_to_cook: boolean;
  missing_count: number;
  estimated_cost: number;
  components_count: number;
}

export default function PlansPage() {
  const [plans, setPlans] = useState<PlanItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [customIntent, setCustomIntent] = useState("");
  const [reconciling, setReconciling] = useState(false);
  const [customResult, setCustomResult] = useState<any>(null);
  const [actionPlanId, setActionPlanId] = useState<string | null>(null);
  const [actionDoneId, setActionDoneId] = useState<string | null>(null);

  const loadPlans = useCallback(async () => {
    try {
      const res = await fetch("/api/plans");
      const data = await res.json();
      setPlans(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load plans:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadPlans();
    const refresh = () => loadPlans();
    window.addEventListener("household-updated", refresh);
    return () => window.removeEventListener("household-updated", refresh);
  }, [loadPlans]);

  const handleTakeCareOf = async (plan: PlanItem) => {
    setActionPlanId(plan.plan_id);
    try {
      await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: `Take care of ${plan.title} - order missing ingredients` }),
      });
      setActionDoneId(plan.plan_id);
      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("cart-updated"));
      window.dispatchEvent(new Event("budget-updated"));
      setTimeout(() => {
        loadPlans();
      }, 1200);
    } finally {
      setActionPlanId(null);
    }
  };

  const handleCustomReconcile = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customIntent.trim() || reconciling) return;
    setReconciling(true);
    setCustomResult(null);

    try {
      const res = await fetch("/api/plans/reconcile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: customIntent.trim() }),
      });
      const data = await res.json();
      setCustomResult(data);
    } catch (err) {
      console.error("Reconciliation failed:", err);
    } finally {
      setReconciling(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF8] text-neutral-900 pt-6 pb-28 font-sans">
      <div className="max-w-4xl mx-auto px-4 sm:px-6">

        {/* ── Breadcrumb & Header ────────────────────────────────────── */}
        <div className="pt-6 pb-6">
          <div className="flex items-center gap-2 text-xs text-neutral-400 font-semibold uppercase tracking-wider mb-1">
            <Link href="/" className="hover:text-neutral-700">Home</Link>
            <span>/</span>
            <span className="text-neutral-900">Household Plans</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-neutral-950 tracking-tight">
            Meal &amp; Household Plans
          </h1>
          <p className="text-neutral-500 text-sm mt-1">
            NOVA reconciles recipe requirements against your live pantry stock so you only order what is missing.
          </p>
        </div>

        {/* ── Custom Meal Intent Input ───────────────────────────────── */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-5 sm:p-6 mb-8 shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold text-neutral-400 uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5 text-amber-500" />
            <span>Plan Anything Tonight</span>
          </div>
          
          <form onSubmit={handleCustomReconcile} className="flex gap-2">
            <input
              type="text"
              value={customIntent}
              onChange={(e) => setCustomIntent(e.target.value)}
              placeholder="e.g. 'I want to make pasta for 4 people tonight', 'Prepare evening chai'..."
              className="flex-1 bg-neutral-50 rounded-2xl px-4 py-3 text-sm border border-neutral-200 outline-none focus:bg-white focus:border-neutral-900 transition-all placeholder:text-neutral-400"
            />
            <button
              type="submit"
              disabled={reconciling || !customIntent.trim()}
              className="px-5 py-3 rounded-2xl bg-neutral-950 hover:bg-neutral-800 disabled:opacity-40 text-white text-xs font-bold transition-all shadow-xs cursor-pointer flex items-center gap-1.5 shrink-0"
            >
              {reconciling ? (
                <>
                  <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                  <span>Checking pantry…</span>
                </>
              ) : (
                <>
                  <span>Check Pantry</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </form>

          {/* Custom Reconciliation Result */}
          {customResult && (
            <div className="mt-4 p-4 rounded-2xl bg-[#F9F9F8] border border-neutral-200 text-xs">
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-sm text-neutral-900">
                  {customResult.recipe?.name || "Reconciled Plan"}
                </span>
                <span className="px-2 py-0.5 rounded-full font-bold bg-amber-100 text-amber-800">
                  {customResult.missing_items?.length || 0} items needed
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-3">
                <div>
                  <p className="font-semibold text-neutral-600 mb-1.5">Already in pantry:</p>
                  <div className="space-y-1">
                    {customResult.available_in_pantry?.map((item: any, i: number) => (
                      <div key={i} className="flex items-center gap-2 text-neutral-700">
                        <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span>{item.item}</span>
                        <span className="text-neutral-400">({item.summary || "In stock"})</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <p className="font-semibold text-neutral-600 mb-1.5">Needed from store:</p>
                  <div className="grid grid-cols-1 gap-3">
                    {customResult.missing_items?.map((item: any, i: number) => (
                      <div key={i} className="flex items-start gap-3 bg-white p-2.5 rounded-xl border border-neutral-100 shadow-sm">
                        {item.product?.image ? (
                           <div className="w-12 h-12 rounded-lg bg-neutral-100 overflow-hidden shrink-0">
                             <img src={item.product.image} alt={item.product.name} className="w-full h-full object-cover" />
                           </div>
                        ) : (
                          <div className="w-12 h-12 rounded-lg bg-amber-50 flex items-center justify-center shrink-0">
                            <ShoppingBag className="w-5 h-5 text-amber-500" />
                          </div>
                        )}
                        <div>
                          <p className="text-sm font-bold text-neutral-900 leading-tight">
                            {item.product ? item.product.name : item.item}
                          </p>
                          {item.product && (
                            <p className="text-xs text-neutral-500 mt-0.5">₹{item.product.price}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── Curated Household Plans Grid ───────────────────────────── */}
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
            Curated Meal &amp; Household Plans
          </h2>
          <span className="text-xs text-neutral-500 font-medium">{plans.length} available</span>
        </div>

        {loading ? (
          <div className="bg-white rounded-3xl border border-neutral-200 p-12 text-center">
            <div className="w-8 h-8 border-3 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mx-auto mb-3" />
            <p className="text-xs text-neutral-500">Checking pantry ingredients…</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {plans.map((plan) => {
              const isActing = actionPlanId === plan.plan_id;
              const isDone = actionDoneId === plan.plan_id;

              return (
                <div
                  key={plan.plan_id}
                  className="bg-white rounded-3xl border border-neutral-200/90 p-5 sm:p-6 shadow-xs flex flex-col justify-between hover:border-neutral-300 transition-all"
                >
                  <div>
                    <div className="flex items-start justify-between gap-3 mb-3">
                      <div>
                        <div className="flex items-center gap-1.5 text-xs font-bold text-amber-600 mb-1">
                          <UtensilsCrossed className="w-3.5 h-3.5" />
                          <span>Household Plan</span>
                        </div>
                        <h3 className="text-lg font-bold text-neutral-950">
                          {plan.title}
                        </h3>
                      </div>
                      <div className="text-right shrink-0">
                        <span className="text-[10px] text-neutral-400 font-bold uppercase block">Est. Cost</span>
                        <span className="text-base font-extrabold text-neutral-950">
                          ₹{plan.estimated_cost}
                        </span>
                      </div>
                    </div>

                    {/* Component breakdown */}
                    <div className="my-4 p-3.5 rounded-2xl bg-[#F9F9F8] border border-neutral-100 text-xs space-y-3">
                      <div>
                        <span className="font-bold text-neutral-600 text-[11px] uppercase tracking-wider block mb-1">
                          In Pantry ({plan.have_items.length})
                        </span>
                        <div className="space-y-1">
                          {plan.have_items.map((h, i) => (
                            <div key={i} className="flex items-center gap-2 text-neutral-700">
                              <Check className="w-3.5 h-3.5 text-emerald-600 shrink-0 stroke-[3]" />
                              <span>{h.item}</span>
                              <span className="text-neutral-400 text-[11px]">({h.stock})</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {plan.need_items.length > 0 && (
                        <div className="pt-2 border-t border-neutral-200/60">
                          <span className="font-bold text-neutral-900 text-[11px] uppercase tracking-wider block mb-1">
                            Needed ({plan.need_items.length})
                          </span>
                          <div className="space-y-1">
                            {plan.need_items.map((n, i) => (
                              <div key={i} className="flex items-center justify-between text-neutral-900 font-semibold">
                                <div className="flex items-center gap-2">
                                  <div className="w-2 h-2 rounded-full bg-amber-500 shrink-0" />
                                  <span>{n.item}</span>
                                </div>
                                <span className="text-neutral-500 font-normal">₹{n.estimated_price}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Action footer */}
                  <div className="flex items-center justify-between pt-3 border-t border-neutral-100">
                    <span className="text-xs text-neutral-500">
                      {plan.missing_count === 0 ? "All items in stock" : `${plan.missing_count} item missing`}
                    </span>

                    <button
                      type="button"
                      onClick={() => handleTakeCareOf(plan)}
                      disabled={isActing || isDone}
                      className={`px-4 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shadow-xs cursor-pointer ${
                        isDone
                          ? "bg-emerald-100 text-emerald-800"
                          : "bg-neutral-950 hover:bg-neutral-800 text-white"
                      }`}
                    >
                      {isActing ? (
                        <>
                          <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                          <span>Ordering…</span>
                        </>
                      ) : isDone ? (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>Taken care of!</span>
                        </>
                      ) : (
                        <>
                          <Zap className="w-3.5 h-3.5 text-amber-400" />
                          <span>Take care of it</span>
                        </>
                      )}
                    </button>
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
