"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Eye,
  Bot,
  AlertTriangle,
  Home,
  Check,
  HelpCircle,
  Clock,
  TrendingDown,
  ShoppingBag,
  CheckCircle2,
  ArrowRight,
  RefreshCw,
} from "lucide-react";

const ANALYSIS_STEPS = [
  { label: "Checking your usual purchases", delay: 400 },
  { label: "Estimating quantities for September", delay: 900 },
  { label: "Checking current household inventory", delay: 1400 },
  { label: "Searching catalog for best prices", delay: 2000 },
  { label: "Applying your household preferences", delay: 2600 },
  { label: "Checking ₹5,500 monthly budget", delay: 3100 },
  { label: "Evaluating household rules", delay: 3600 },
  { label: "Preparing your NOVA Cart", delay: 4100 },
];

export default function AutopilotPage() {
  const router = useRouter();
  const [phase, setPhase] = useState<"idle" | "analyzing" | "done">("idle");
  const [stepsCompleted, setStepsCompleted] = useState<number>(0);
  const [plan, setPlan] = useState<any>(null);
  const [approvedItems, setApprovedItems] = useState<Set<string>>(new Set());
  const [mode, setMode] = useState<"ASSISTED" | "AUTOPILOT">("ASSISTED");
  const [syncing, setSyncing] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);

  const runAutopilot = async () => {
    setPhase("analyzing");
    setStepsCompleted(0);
    setPlan(null);

    // Animate steps with delays
    for (let i = 0; i < ANALYSIS_STEPS.length; i++) {
      await new Promise((resolve) =>
        setTimeout(resolve, ANALYSIS_STEPS[i].delay - (i > 0 ? ANALYSIS_STEPS[i - 1].delay : 0))
      );
      setStepsCompleted(i + 1);
    }

    // Fetch the actual plan from backend
    const data = await fetch("/api/autopilot/monthly-plan", { method: "POST" })
      .then((r) => r.json())
      .catch(() => null);

    setPlan(data);
    setPhase("done");
  };

  const handleApproveItem = async (productId: string) => {
    await fetch("/api/autopilot/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, approved: true }),
    });
    setApprovedItems((prev) => {
      const next = new Set(prev);
      next.add(productId);
      return next;
    });
  };

  const handleSendToCart = async () => {
    setSyncing(true);
    try {
      const itemsToAdd =
        plan?.items?.filter(
          (item: any) => item.decision === "AUTO" || approvedItems.has(item.product_id)
        ) || [];
      for (const item of itemsToAdd) {
        await fetch("/api/cart/add", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ product_id: item.product_id, quantity: item.typical_quantity || 1 }),
        }).catch(() => {});
      }
      setSyncSuccess(true);
      window.dispatchEvent(new Event("cart-updated"));
      setTimeout(() => {
        router.push("/cart");
      }, 1200);
    } catch (err) {
      console.error(err);
    } finally {
      setSyncing(false);
    }
  };

  const autoCount = plan?.stats?.auto_count || 0;
  const askCount = plan?.stats?.ask_count || 0;
  const waitCount = plan?.stats?.wait_count || 0;
  const total = plan?.total_estimated || 0;
  const budget = plan?.budget || 5500;
  const remaining = budget - total;

  return (
    <div className="min-h-screen bg-neutral-50 pb-20">
      <div className="max-w-4xl mx-auto px-4 pt-10">
        {/* Header */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-2">Household Autopilot</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Monthly Autopilot</h1>
          <p className="text-neutral-500">Let NOVA prepare your usual household order with deterministic safety.</p>
        </div>

        {/* Mode toggle */}
        <div className="flex gap-3 mb-8">
          {(["ASSISTED", "AUTOPILOT"] as const).map((m) => (
            <button
              key={m}
              onClick={() => setMode(m)}
              className={`flex-1 py-3 px-4 rounded-2xl border-2 font-semibold text-sm transition-all ${
                mode === m
                  ? "border-neutral-900 bg-neutral-900 text-white"
                  : "border-neutral-200 bg-white text-neutral-600 hover:border-neutral-400"
              }`}
            >
              <span className="flex items-center justify-center gap-2 text-base">
                {m === "ASSISTED" ? <Eye className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                {m === "ASSISTED" ? "Assisted" : "Autopilot"}
              </span>
              <span className="block text-xs font-normal mt-0.5 opacity-70">
                {m === "ASSISTED" ? "You approve the final cart" : "NOVA handles routine items automatically"}
              </span>
            </button>
          ))}
        </div>

        {/* Current limits display */}
        {mode === "AUTOPILOT" && (
          <div className="mb-8 p-5 bg-orange-50 border border-orange-100 rounded-2xl">
            <p className="text-sm font-bold text-orange-900 mb-3">Autopilot rules</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {[
                { label: "Max per item", value: "₹500" },
                { label: "Monthly limit", value: "₹5,500" },
                { label: "Preferred retailer", value: "Swiggy Instamart" },
                { label: "Categories", value: "Grocery + Household" },
              ].map((r) => (
                <div key={r.label} className="bg-white rounded-xl p-3 border border-orange-100">
                  <p className="text-xs text-neutral-500">{r.label}</p>
                  <p className="text-sm font-bold text-neutral-900 mt-0.5">{r.value}</p>
                </div>
              ))}
            </div>
            <div className="mt-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-orange-500 shrink-0" />
              <p className="text-xs text-orange-700">
                NOVA will ask for your approval on any item above ₹500 or outside routine purchases.
              </p>
            </div>
          </div>
        )}

        {/* Trigger button */}
        {phase === "idle" && (
          <div className="bg-white rounded-3xl border border-neutral-200 p-8 text-center">
            <div className="w-16 h-16 bg-[#FF9900]/10 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <Home className="w-8 h-8 text-[#FF9900]" />
            </div>
            <h2 className="text-xl font-black text-neutral-900 mb-2">Handle my monthly grocery shopping</h2>
            <p className="text-neutral-500 text-sm mb-6 max-w-sm mx-auto">
              NOVA will analyze your household purchase history, check inventory, compare prices, and prepare your household cart.
            </p>
            <button
              onClick={runAutopilot}
              className="inline-flex items-center gap-2 px-8 py-4 bg-[#FF9900] text-white font-bold rounded-2xl hover:bg-[#e68900] transition-all hover:scale-105 active:scale-95 text-base shadow-md"
            >
              Start Monthly Autopilot <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        )}

        {/* Analysis stream */}
        {(phase === "analyzing" || phase === "done") && (
          <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-6">
            <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-4">NOVA Analysis</p>
            <div className="space-y-2.5">
              {ANALYSIS_STEPS.map((step, i) => {
                const done = stepsCompleted > i;
                const active = stepsCompleted === i && phase === "analyzing";
                return (
                  <div
                    key={i}
                    className={`flex items-center gap-3 transition-all ${
                      done || active ? "opacity-100" : "opacity-30"
                    }`}
                  >
                    <div
                      className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 transition-all ${
                        done ? "bg-green-500" : active ? "bg-[#FF9900] animate-pulse" : "bg-neutral-200"
                      }`}
                    >
                      {done ? (
                        <Check className="w-3 h-3 text-white" />
                      ) : active ? (
                        <div className="w-2 h-2 rounded-full bg-white animate-pulse"></div>
                      ) : (
                        <div className="w-2 h-2 rounded-full bg-neutral-300"></div>
                      )}
                    </div>
                    <p className={`text-sm ${done ? "text-neutral-900 font-medium" : "text-neutral-500"}`}>
                      {step.label}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Plan results */}
        {phase === "done" && plan && (
          <>
            {/* Summary cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              {[
                { label: "Automatic", value: String(autoCount), color: "green", sub: "items" },
                { label: "Needs approval", value: String(askCount), color: "orange", sub: "items" },
                { label: "Waiting", value: String(waitCount), color: "blue", sub: "price watch" },
                {
                  label: "Estimated total",
                  value: `₹${total.toLocaleString("en-IN")}`,
                  color: "neutral",
                  sub: `of ₹${budget.toLocaleString("en-IN")}`,
                },
              ].map((s) => (
                <div
                  key={s.label}
                  className={`p-4 rounded-2xl border ${
                    s.color === "green"
                      ? "bg-green-50 border-green-100"
                      : s.color === "orange"
                      ? "bg-orange-50 border-orange-100"
                      : s.color === "blue"
                      ? "bg-blue-50 border-blue-100"
                      : "bg-white border-neutral-200"
                  }`}
                >
                  <p
                    className={`text-2xl font-black ${
                      s.color === "green"
                        ? "text-green-700"
                        : s.color === "orange"
                        ? "text-orange-700"
                        : s.color === "blue"
                        ? "text-blue-700"
                        : "text-neutral-900"
                    }`}
                  >
                    {s.value}
                  </p>
                  <p
                    className={`text-xs font-semibold mt-0.5 ${
                      s.color === "green"
                        ? "text-green-600"
                        : s.color === "orange"
                        ? "text-orange-600"
                        : s.color === "blue"
                        ? "text-blue-600"
                        : "text-neutral-500"
                    }`}
                  >
                    {s.label}
                  </p>
                  <p className="text-[10px] text-neutral-400">{s.sub}</p>
                </div>
              ))}
            </div>

            {/* Budget bar */}
            <div className="bg-white rounded-2xl border border-neutral-200 p-5 mb-6">
              <div className="flex justify-between items-center mb-3">
                <p className="text-sm font-semibold text-neutral-700">Monthly budget</p>
                <p className="text-sm font-bold text-neutral-900">₹{budget.toLocaleString("en-IN")}</p>
              </div>
              <div className="w-full h-3 bg-neutral-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-1000 ${
                    total / budget > 0.9 ? "bg-red-500" : "bg-[#FF9900]"
                  }`}
                  style={{ width: `${Math.min(100, (total / budget) * 100)}%` }}
                ></div>
              </div>
              <div className="flex justify-between mt-2">
                <p className="text-xs text-neutral-500">Estimated: ₹{total.toLocaleString("en-IN")}</p>
                <p
                  className={`text-xs font-semibold ${
                    remaining >= 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {remaining >= 0
                    ? `₹${remaining.toLocaleString("en-IN")} remaining`
                    : `₹${Math.abs(remaining).toLocaleString("en-IN")} over budget`}
                </p>
              </div>
            </div>

            {/* Item list */}
            <div className="space-y-3 mb-8">
              {plan.items.map((item: any) => {
                const approved = approvedItems.has(item.product_id);
                return (
                  <div
                    key={item.product_id}
                    className={`bg-white rounded-2xl border p-4 ${
                      item.decision === "ASK" && !approved
                        ? "border-orange-200"
                        : item.decision === "WAIT"
                        ? "border-blue-200"
                        : "border-neutral-200"
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm ${
                          item.decision === "AUTO" || approved
                            ? "bg-green-100"
                            : item.decision === "ASK"
                            ? "bg-orange-100"
                            : "bg-blue-100"
                        }`}
                      >
                        {item.decision === "AUTO" || approved ? (
                          <Check className="w-4 h-4 text-green-700" />
                        ) : item.decision === "ASK" ? (
                          <HelpCircle className="w-4 h-4 text-orange-700" />
                        ) : (
                          <Clock className="w-4 h-4 text-blue-700" />
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="text-sm font-semibold text-neutral-900">{item.name}</p>
                          <span className="text-[10px] text-neutral-400">{item.pack_size}</span>
                          <span
                            className={`text-[9px] font-bold px-2 py-0.5 rounded-full ${
                              item.decision === "AUTO" || approved
                                ? "bg-green-100 text-green-700"
                                : item.decision === "ASK"
                                ? "bg-orange-100 text-orange-700"
                                : "bg-blue-100 text-blue-700"
                            }`}
                          >
                            {approved
                              ? "APPROVED"
                              : item.decision === "AUTO"
                              ? "AUTO"
                              : item.decision === "ASK"
                              ? "NEEDS OK"
                              : "WAIT"}
                          </span>
                        </div>
                        <p className="text-xs text-neutral-500 mt-0.5">{item.reason}</p>
                        <div className="flex items-center gap-3 mt-2">
                          <span className="text-sm font-bold text-neutral-900">₹{item.current_price}</span>
                          {item.avg_price && item.current_price < item.avg_price && (
                            <span className="text-xs text-green-600 font-semibold flex items-center gap-1">
                              <TrendingDown className="w-3.5 h-3.5" /> Below avg
                            </span>
                          )}
                          <span className="text-xs text-neutral-400">Qty: {item.typical_quantity}</span>
                        </div>
                      </div>
                      {item.decision === "ASK" && !approved && (
                        <button
                          onClick={() => handleApproveItem(item.product_id)}
                          className="px-4 py-2 bg-[#FF9900] text-white text-xs font-bold rounded-xl hover:bg-[#e68900] transition-colors shrink-0"
                        >
                          Approve
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Final CTA */}
            <div className="bg-white rounded-3xl border border-neutral-200 p-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <p className="text-sm text-neutral-500 mb-1">
                    {autoCount} items automatic &middot; {Math.max(0, askCount - approvedItems.size)} still need approval
                  </p>
                  <p className="text-xl font-black text-neutral-900">Household cart ready</p>
                </div>
                <div className="flex flex-col gap-2">
                  <button
                    disabled={syncing}
                    className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-[#FF9900] text-white font-bold rounded-xl hover:bg-[#e68900] transition-colors text-sm disabled:opacity-50"
                    onClick={handleSendToCart}
                  >
                    {syncing ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" /> Synchronizing Cart...
                      </>
                    ) : syncSuccess ? (
                      <>
                        <CheckCircle2 className="w-4 h-4" /> Cart Synchronized! Redirecting...
                      </>
                    ) : (
                      <>
                        <ShoppingBag className="w-4 h-4" /> Send to Commerce Cart &rarr;
                      </>
                    )}
                  </button>
                  <p className="text-xs text-center text-neutral-400">Deterministic validation &middot; Budget protected</p>
                </div>
              </div>
            </div>
          </>
        )}

        {/* NOVA money control note */}
        <div className="mt-6 p-4 bg-neutral-50 rounded-2xl border border-neutral-200">
          <p className="text-xs text-neutral-500 leading-relaxed">
            <strong className="text-neutral-700">NOVA can prepare the order. You control the money.</strong>{" "}
            Nothing outside your rules can be purchased automatically. All purchases above ₹500 require your explicit approval.
          </p>
        </div>
      </div>
    </div>
  );
}
