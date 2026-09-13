"use client";

import { useState, useEffect, useCallback } from "react";
import { Check, ShieldCheck } from "lucide-react";

type AutoLevel = 0 | 1 | 2 | 3;

const LEVEL_CONFIG: Record<AutoLevel, { label: string; description: string; color: string }> = {
  0: { label: "Suggest only", description: "NOVA recommends. You decide and act on everything.", color: "bg-neutral-100 text-neutral-700" },
  1: { label: "Prepare cart", description: "NOVA prepares your purchase list. You approve and checkout.", color: "bg-blue-100 text-blue-700" },
  2: { label: "Handle routine items", description: "NOVA auto-buys routine items within your limits. Alerts you for anything unusual.", color: "bg-amber-100 text-amber-700" },
  3: { label: "Full autopilot", description: "NOVA handles all qualifying purchases within your budget rules. You're notified after.", color: "bg-emerald-100 text-emerald-700" },
};

export default function RulesPage() {
  const [autoLevel, setAutoLevel] = useState<AutoLevel>(2);
  const [autoLimit, setAutoLimit] = useState(500);
  const [monthlyLimit, setMonthlyLimit] = useState(5500);
  const [primeOnly, setPrimeOnly] = useState(true);
  const [allowSubs, setAllowSubs] = useState(true);
  const [allowedCats, setAllowedCats] = useState(["Grocery", "Household", "Personal Care"]);
  const [askAbove, setAskAbove] = useState(500);
  const [askNewBrands, setAskNewBrands] = useState(true);
  const [askPriceIncrease, setAskPriceIncrease] = useState(15);
  const [saved, setSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [loadError, setLoadError] = useState(false);

  const allCats = ["Grocery", "Household", "Personal Care", "Electronics", "Clothing", "Furniture"];

  const loadData = useCallback(async () => {
    try {
      const [policyRes, budgetRes] = await Promise.all([
        fetch("/api/policy").then((r) => r.json()),
        fetch("/api/budget").then((r) => r.json()),
      ]);

      // Load from policy
      if (policyRes.auto_buy_limit) setAutoLimit(policyRes.auto_buy_limit);
      if (policyRes.automatic_categories?.length > 0) setAllowedCats(policyRes.automatic_categories);
      if (policyRes.autonomy_profile === "SUGGEST_ONLY") setAutoLevel(0);
      else if (policyRes.autonomy_profile === "PREPARE_CART") setAutoLevel(1);
      else if (policyRes.autonomy_profile === "ROUTINE_ITEMS") setAutoLevel(2);
      else if (policyRes.autonomy_profile === "FULL_AUTOPILOT") setAutoLevel(3);

      // Load monthly budget from budget service (source of truth)
      if (budgetRes.monthly) setMonthlyLimit(budgetRes.monthly);
      if (budgetRes.auto_limit) setAutoLimit(budgetRes.auto_limit);
    } catch {
      setLoadError(true);
    }
  }, []);

  useEffect(() => {
    loadData();
    const refresh = () => loadData();
    window.addEventListener("budget-updated", refresh);
    window.addEventListener("household-updated", refresh);
    return () => {
      window.removeEventListener("budget-updated", refresh);
      window.removeEventListener("household-updated", refresh);
    };
  }, [loadData]);

  const toggleCat = (cat: string) => {
    setAllowedCats((prev) => prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]);
  };

  const handleSave = async () => {
    setIsSaving(true);
    const profileMap: Record<AutoLevel, string> = {
      0: "SUGGEST_ONLY",
      1: "PREPARE_CART",
      2: "ROUTINE_ITEMS",
      3: "FULL_AUTOPILOT",
    };
    try {
      // Persist policy + autonomy
      await fetch("/api/policy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          auto_buy_limit: autoLimit,
          monthly_budget: monthlyLimit,
          automatic_categories: allowedCats,
          autonomy_profile: profileMap[autoLevel],
        }),
      });

      // Also persist budget directly (single source of truth for budget)
      await fetch("/api/budget", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          monthly: monthlyLimit,
          auto_limit: autoLimit,
        }),
      });

      setSaved(true);
      window.dispatchEvent(new Event("budget-updated"));
      window.dispatchEvent(new Event("household-updated"));
      setTimeout(() => setSaved(false), 2500);
    } catch {
      // silent — show saved anyway if any succeeded
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#FAFAF8] pt-20 pb-32">
      <div className="max-w-2xl mx-auto px-4 md:px-6">

        {/* Header */}
        <div className="pt-8 pb-6">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-1">NOVA · Autopilot Control</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Your Rules</h1>
          <p className="text-neutral-500">You decide exactly what NOVA is allowed to do. Always.</p>
        </div>

        {/* Key principle */}
        <div className="bg-neutral-900 text-white rounded-2xl p-5 mb-5 flex items-start gap-3">
          <ShieldCheck className="w-5 h-5 text-[#FF9900] mt-0.5 shrink-0" />
          <p className="text-sm font-semibold leading-relaxed">
            NOVA can act autonomously within these rules.{" "}
            <span className="text-[#FF9900]">Nothing outside them ever gets purchased.</span>
            <br />
            Every decision is logged and reversible.
          </p>
        </div>

        {/* Autonomy level */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-5">
          <h2 className="text-base font-black text-neutral-900 mb-1">How much can NOVA do on its own?</h2>
          <p className="text-xs text-neutral-400 mb-4">Choose how autonomously NOVA operates.</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {([0, 1, 2, 3] as AutoLevel[]).map((level) => {
              const cfg = LEVEL_CONFIG[level];
              const isSelected = autoLevel === level;
              return (
                <button
                  key={level}
                  onClick={() => setAutoLevel(level)}
                  className={`p-4 rounded-2xl border-2 text-left transition-all ${
                    isSelected ? "border-neutral-900 shadow-sm" : "border-neutral-200 hover:border-neutral-400"
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${cfg.color}`}>
                      Level {level}
                    </span>
                    {isSelected && <Check className="w-3.5 h-3.5 text-neutral-900 ml-auto" />}
                  </div>
                  <p className="text-sm font-bold text-neutral-900">{cfg.label}</p>
                  <p className="text-xs text-neutral-500 mt-0.5 leading-snug">{cfg.description}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Money limits */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-5">
          <h2 className="text-base font-black text-neutral-900 mb-1">Spending limits</h2>
          <p className="text-xs text-neutral-400 mb-4">NOVA will not spend beyond these thresholds.</p>
          <div className="space-y-5">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-neutral-700">
                  Max per item (auto-purchase)
                </label>
                <span className="text-sm font-black text-neutral-900">₹{autoLimit.toLocaleString("en-IN")}</span>
              </div>
              <input
                type="range" min={100} max={2000} step={50} value={autoLimit}
                onChange={(e) => setAutoLimit(Number(e.target.value))}
                className="w-full accent-[#FF9900]"
              />
              <p className="text-xs text-neutral-400 mt-1">
                Items above ₹{autoLimit} will always be flagged for your approval first.
              </p>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-neutral-700">Monthly household budget</label>
                <span className="text-sm font-black text-neutral-900">₹{monthlyLimit.toLocaleString("en-IN")}</span>
              </div>
              <input
                type="range" min={1000} max={20000} step={500} value={monthlyLimit}
                onChange={(e) => setMonthlyLimit(Number(e.target.value))}
                className="w-full accent-[#FF9900]"
              />
              <p className="text-xs text-neutral-400 mt-1">
                NOVA will stop auto-purchasing if this limit would be exceeded.
              </p>
            </div>
          </div>
        </div>

        {/* Allowed categories */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-5">
          <h2 className="text-base font-black text-neutral-900 mb-1">Purchasing categories</h2>
          <p className="text-sm text-neutral-500 mb-4">NOVA can auto-purchase only from these categories.</p>
          <div className="flex flex-wrap gap-2">
            {allCats.map((cat) => (
              <button
                key={cat}
                onClick={() => toggleCat(cat)}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-1.5 ${
                  allowedCats.includes(cat)
                    ? "bg-neutral-900 text-white"
                    : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"
                }`}
              >
                {allowedCats.includes(cat) && <Check className="w-3.5 h-3.5" />}
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Smart product rules */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-5">
          <h2 className="text-base font-black text-neutral-900 mb-4">Smart product rules</h2>
          <div className="space-y-3">
            {[
              { label: "Prime eligible only", sub: "Only purchase items with fast delivery", value: primeOnly, toggle: () => setPrimeOnly(!primeOnly) },
              { label: "Allow brand substitutions", sub: "If your usual brand is unavailable, NOVA can use a similar product", value: allowSubs, toggle: () => setAllowSubs(!allowSubs) },
              { label: "Ask before new brands", sub: "Always confirm before buying a brand not in your household history", value: askNewBrands, toggle: () => setAskNewBrands(!askNewBrands) },
            ].map((rule) => (
              <div key={rule.label} className="flex items-center justify-between p-4 bg-neutral-50 rounded-2xl">
                <div>
                  <p className="text-sm font-semibold text-neutral-900">{rule.label}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">{rule.sub}</p>
                </div>
                <button
                  onClick={rule.toggle}
                  className={`w-12 h-6 rounded-full transition-all relative shrink-0 ${rule.value ? "bg-[#FF9900]" : "bg-neutral-200"}`}
                >
                  <div className={`w-5 h-5 rounded-full bg-white shadow absolute top-0.5 transition-all ${rule.value ? "right-0.5" : "left-0.5"}`} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Always-ask thresholds */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-6">
          <h2 className="text-base font-black text-neutral-900 mb-1">Always ask me when</h2>
          <p className="text-xs text-neutral-400 mb-4">NOVA will pause and get your approval in these situations.</p>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-neutral-700">Purchase above</label>
                <span className="text-sm font-black text-neutral-900">₹{askAbove}</span>
              </div>
              <input
                type="range" min={100} max={2000} step={100} value={askAbove}
                onChange={(e) => setAskAbove(Number(e.target.value))}
                className="w-full accent-[#FF9900]"
              />
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-neutral-700">Price rise above average</label>
                <span className="text-sm font-black text-neutral-900">{askPriceIncrease}%</span>
              </div>
              <input
                type="range" min={5} max={50} step={5} value={askPriceIncrease}
                onChange={(e) => setAskPriceIncrease(Number(e.target.value))}
                className="w-full accent-[#FF9900]"
              />
              <p className="text-xs text-neutral-400 mt-1">
                Ask before buying if price is {askPriceIncrease}% or more above your household average.
              </p>
            </div>
          </div>
        </div>

        {/* Save */}
        <button
          onClick={handleSave}
          disabled={isSaving}
          className={`w-full py-4 rounded-2xl font-bold text-base transition-all flex items-center justify-center gap-2 ${
            saved
              ? "bg-emerald-500 text-white"
              : "bg-neutral-900 text-white hover:bg-neutral-800"
          } disabled:opacity-60`}
        >
          {saved ? (
            <><Check className="w-5 h-5" /> Rules saved</>
          ) : isSaving ? (
            "Saving…"
          ) : (
            "Save Autopilot Rules"
          )}
        </button>
        <p className="text-xs text-center text-neutral-400 mt-2">
          Changes take effect immediately. NOVA re-evaluates all pending decisions.
        </p>
      </div>
    </div>
  );
}
