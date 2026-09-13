"use client";

import { useState, useEffect } from "react";
import { X, Check, Sliders, ShieldCheck, AlertCircle, RefreshCw } from "lucide-react";

interface BudgetModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSaved?: (newBudget: { monthly: number; auto_limit: number; remaining: number; spent: number }) => void;
  initialMonthly?: number;
  initialAutoLimit?: number;
}

export default function BudgetModal({
  isOpen,
  onClose,
  onSaved,
  initialMonthly,
  initialAutoLimit,
}: BudgetModalProps) {
  const [monthly, setMonthly] = useState<number>(initialMonthly || 5500);
  const [autoLimit, setAutoLimit] = useState<number>(initialAutoLimit || 500);
  const [spent, setSpent] = useState<number>(3940);
  const [saving, setSaving] = useState<boolean>(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetch("/api/budget")
        .then((r) => r.json())
        .then((data) => {
          if (data) {
            if (data.monthly) setMonthly(data.monthly);
            if (data.auto_limit) setAutoLimit(data.auto_limit);
            if (data.spent !== undefined) setSpent(data.spent);
          }
        })
        .catch(() => {});
      setStatusMessage(null);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const remaining = monthly - spent;
  const isDeficit = remaining < 0;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatusMessage(null);

    // Validation
    const mNum = Number(monthly);
    const aNum = Number(autoLimit);

    if (isNaN(mNum) || mNum <= 0) {
      setStatusMessage("Please enter a valid monthly budget amount (greater than ₹0).");
      return;
    }
    if (isNaN(aNum) || aNum <= 0) {
      setStatusMessage("Please enter a valid auto-buy limit (greater than ₹0).");
      return;
    }
    if (aNum > mNum) {
      setStatusMessage("Auto-buy limit per order cannot exceed total monthly budget.");
      return;
    }

    setSaving(true);

    try {
      const res = await fetch("/api/budget", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          monthly: mNum,
          auto_limit: aNum,
        }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Failed to update budget");
      }
      const updated = await res.json();

      // Trigger global update events across all open components
      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("budget-updated"));
      window.dispatchEvent(new Event("activity-updated"));

      if (onSaved) {
        onSaved(updated);
      }

      setStatusMessage("Budget updated successfully!");
      setTimeout(() => {
        onClose();
      }, 600);
    } catch (err: any) {
      console.error(err);
      setStatusMessage(err.message || "Failed to save budget settings.");
    } finally {
      setSaving(false);
    }
  };

  const PRESET_BUDGETS = [4000, 5500, 7500, 10000];
  const PRESET_LIMITS = [300, 500, 800, 1200];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div 
        className="bg-white rounded-2xl shadow-2xl border border-neutral-200 w-full max-w-lg overflow-hidden transform transition-all"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="px-6 py-4 bg-[#131921] text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#FF9900] text-[#131921] flex items-center justify-center font-bold">
              <Sliders className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white">Adjust Household Budget</h2>
              <p className="text-xs text-neutral-300">NOVA Autopilot Safety & Spending Limits</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-neutral-400 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <form onSubmit={handleSave} className="p-6 space-y-6">
          {/* Monthly Budget Section */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-sm font-bold text-neutral-900">
                Monthly Household Budget
              </label>
              <span className="text-base font-black text-neutral-900">
                ₹{Number(monthly || 0).toLocaleString("en-IN")}
              </span>
            </div>
            <p className="text-xs text-neutral-500 mb-3">
              Total cap for automated replenishment and household groceries.
            </p>

            <div className="flex gap-2 mb-3">
              {PRESET_BUDGETS.map((amt) => (
                <button
                  key={amt}
                  type="button"
                  onClick={() => setMonthly(amt)}
                  className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold border transition-all ${
                    monthly === amt
                      ? "bg-[#FF9900]/15 border-[#FF9900] text-[#131921] font-bold"
                      : "bg-neutral-50 hover:bg-neutral-100 border-neutral-200 text-neutral-700"
                  }`}
                >
                  ₹{amt.toLocaleString("en-IN")}
                </button>
              ))}
            </div>

            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-sm font-bold text-neutral-500">
                ₹
              </span>
              <input
                type="number"
                min="500"
                max="100000"
                step="100"
                value={monthly}
                onChange={(e) => setMonthly(Number(e.target.value))}
                className="w-full pl-8 pr-4 py-2.5 rounded-xl border border-neutral-300 text-sm font-semibold text-neutral-900 focus:outline-none focus:ring-2 focus:ring-[#FF9900] focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Auto-buy Limit Section */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="text-sm font-bold text-neutral-900">
                Autonomous Buy Limit per Item
              </label>
              <span className="text-base font-black text-neutral-900">
                ₹{Number(autoLimit || 0).toLocaleString("en-IN")}
              </span>
            </div>
            <p className="text-xs text-neutral-500 mb-3">
              Items priced higher than this require explicit user confirmation before order.
            </p>

            <div className="flex gap-2 mb-3">
              {PRESET_LIMITS.map((amt) => (
                <button
                  key={amt}
                  type="button"
                  onClick={() => setAutoLimit(amt)}
                  className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold border transition-all ${
                    autoLimit === amt
                      ? "bg-[#FF9900]/15 border-[#FF9900] text-[#131921] font-bold"
                      : "bg-neutral-50 hover:bg-neutral-100 border-neutral-200 text-neutral-700"
                  }`}
                >
                  ₹{amt.toLocaleString("en-IN")}
                </button>
              ))}
            </div>

            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-sm font-bold text-neutral-500">
                ₹
              </span>
              <input
                type="number"
                min="50"
                max="10000"
                step="50"
                value={autoLimit}
                onChange={(e) => setAutoLimit(Number(e.target.value))}
                className="w-full pl-8 pr-4 py-2.5 rounded-xl border border-neutral-300 text-sm font-semibold text-neutral-900 focus:outline-none focus:ring-2 focus:ring-[#FF9900] focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Real-time Math Summary Card */}
          <div className="bg-neutral-50 border border-neutral-200 rounded-xl p-4 space-y-2 text-xs">
            <div className="flex justify-between items-center text-neutral-600">
              <span>Spent This Month:</span>
              <span className="font-semibold text-neutral-900">₹{spent.toLocaleString("en-IN")}</span>
            </div>
            <div className="flex justify-between items-center pt-2 border-t border-neutral-200">
              <span className="font-bold text-neutral-900">Projected Remaining:</span>
              <span className={`text-sm font-black ${isDeficit ? "text-red-600" : "text-emerald-700"}`}>
                ₹{remaining.toLocaleString("en-IN")}
              </span>
            </div>
            {isDeficit && (
              <div className="flex items-center gap-1.5 text-red-600 text-[11px] pt-1">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>Current spending exceeds this budget amount.</span>
              </div>
            )}
          </div>

          {statusMessage && (
            <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2">
              <Check className="w-4 h-4 text-emerald-600" />
              <span>{statusMessage}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="px-4 py-2 text-xs font-semibold text-neutral-600 hover:text-neutral-900 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2.5 bg-[#FF9900] hover:bg-[#e68900] text-[#131921] font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-2"
            >
              {saving ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <ShieldCheck className="w-4 h-4" />
                  Save Household Budget
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
