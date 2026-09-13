"use client";

import { useState, useEffect, useCallback } from "react";
import {
  AlertCircle,
  CheckCircle2,
  MinusCircle,
  Clock,
  HelpCircle,
  RotateCcw,
  Zap,
  ChevronDown,
  ChevronUp,
  Send,
} from "lucide-react";

interface PantryItem {
  product_id: string;
  name: string;
  quantity: number;
  unit: string;
  daily_consumption: number;
  days_remaining: number;
  status: string;
  urgency: string;
  category: string;
  confidence: number;
  confidence_score: string;
  confidence_level: string;
  preferred: boolean;
  last_updated: string | null;
}

function ConfidenceBar({ value, level }: { value: number; level: string }) {
  const pct = Math.round(value * 100);
  const color =
    pct >= 85
      ? "bg-emerald-500"
      : pct >= 65
      ? "bg-amber-400"
      : "bg-red-400";
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-1.5 bg-neutral-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className={`text-xs font-semibold ${pct >= 85 ? "text-emerald-600" : pct >= 65 ? "text-amber-500" : "text-red-500"}`}>
        {pct}% · {level}
      </span>
    </div>
  );
}

function DaysLabel({ days }: { days: number }) {
  if (days <= 0) return <span className="text-red-600 font-bold text-sm">Depleted</span>;
  if (days <= 1) return <span className="text-red-600 font-bold text-sm">~Today</span>;
  if (days <= 2) return <span className="text-orange-600 font-bold text-sm">~Tomorrow</span>;
  return <span className="text-neutral-700 font-bold text-sm">~{Math.ceil(days)} days</span>;
}

function SectionHeader({ icon, title, count, color }: { icon: React.ReactNode; title: string; count: number; color: string }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      {icon}
      <h2 className={`text-xs font-bold tracking-widest uppercase ${color}`}>{title}</h2>
      <span className="text-xs font-bold bg-neutral-100 text-neutral-500 rounded-full px-2 py-0.5">{count}</span>
    </div>
  );
}

export default function PantryPage() {
  const [items, setItems] = useState<PantryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [copilotQuery, setCopilotQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentFeedback, setAgentFeedback] = useState<string | null>(null);
  const [actionItem, setActionItem] = useState<string | null>(null);
  const [showComfortable, setShowComfortable] = useState(false);

  const fetchPantry = useCallback(async () => {
    try {
      const res = await fetch("/api/pantry");
      const data = await res.json();
      setItems(Array.isArray(data) ? data : []);
    } catch {
      /* keep previous */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPantry();
    const refresh = () => fetchPantry();
    window.addEventListener("household-updated", refresh);
    return () => window.removeEventListener("household-updated", refresh);
  }, [fetchPantry]);

  const handleCopilotSubmit = async (queryToRun?: string) => {
    const query = (queryToRun || copilotQuery).trim();
    if (!query) return;
    setIsProcessing(true);
    setAgentFeedback(null);
    try {
      const res = await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: query }),
      });
      const data = await res.json();
      setAgentFeedback(data.response || "Pantry updated.");
      setCopilotQuery("");
      window.dispatchEvent(new Event("household-updated"));
      await fetchPantry();
    } catch {
      setAgentFeedback("Couldn't reach NOVA right now.");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTakeCareOf = async (item: PantryItem) => {
    setActionItem(item.product_id);
    try {
      const prompt = `Take care of ${item.name} — ${item.quantity} ${item.unit} left (~${item.days_remaining} days). Please check if I need it and handle it.`;
      const res = await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: prompt }),
      });
      const data = await res.json();
      setAgentFeedback(data.response || "Done.");
      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("cart-updated"));
      await fetchPantry();
    } finally {
      setActionItem(null);
    }
  };

  // Group items by urgency
  const urgent = items.filter((i) => i.urgency === "URGENT");
  const upcoming = items.filter((i) => i.urgency === "UPCOMING");
  const comfortable = items.filter((i) => i.urgency === "COMFORTABLE");
  const uncertain = items.filter((i) => i.urgency === "UNCERTAIN");

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAFAF8] flex items-center justify-center pt-20">
        <div className="w-10 h-10 border-4 border-neutral-200 border-t-neutral-800 rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF8] pt-20 pb-32">
      <div className="max-w-2xl mx-auto px-4 md:px-6">

        {/* Header */}
        <div className="pt-8 pb-6">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-1">NOVA · Household Pantry</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Pantry</h1>
          <p className="text-neutral-500">
            Tracking {items.length} essentials.
            {urgent.length > 0 && (
              <span className="text-red-600 font-semibold"> {urgent.length} need attention.</span>
            )}
          </p>
        </div>

        {/* Copilot */}
        <div className="bg-white rounded-2xl border border-neutral-200 p-4 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">NOVA Pantry Copilot</p>
          </div>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="'We ran out of tea', 'Add 2L of milk', 'Check if we need oil'…"
              value={copilotQuery}
              onChange={(e) => setCopilotQuery(e.target.value)}
              disabled={isProcessing}
              onKeyDown={(e) => e.key === "Enter" && handleCopilotSubmit()}
              className="flex-1 px-3.5 py-2.5 bg-neutral-50 border border-neutral-200 rounded-xl text-sm focus:outline-none focus:border-neutral-800 transition-colors placeholder:text-neutral-400"
            />
            <button
              onClick={() => handleCopilotSubmit()}
              disabled={isProcessing || !copilotQuery.trim()}
              className="px-4 py-2.5 bg-neutral-900 text-white text-sm font-bold rounded-xl hover:bg-neutral-800 transition-colors disabled:opacity-40 flex items-center gap-1.5"
            >
              {isProcessing ? <RotateCcw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            </button>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-2.5">
            {["We ran out of tea", "Add 2L of milk", "Check if we need oil", "Ran out of salt"].map((chip) => (
              <button
                key={chip}
                type="button"
                onClick={() => handleCopilotSubmit(chip)}
                disabled={isProcessing}
                className="px-2.5 py-1 bg-neutral-100 hover:bg-neutral-200 text-neutral-600 text-xs font-semibold rounded-lg transition-colors"
              >
                {chip}
              </button>
            ))}
          </div>
          {agentFeedback && (
            <div className="mt-3 p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-sm text-emerald-900 leading-relaxed">
              <span className="font-bold block mb-0.5 text-emerald-950">NOVA:</span>
              {agentFeedback}
            </div>
          )}
        </div>

        {/* URGENT */}
        {urgent.length > 0 && (
          <section className="mb-6">
            <SectionHeader
              icon={<AlertCircle className="w-4 h-4 text-red-500" />}
              title="Running low"
              count={urgent.length}
              color="text-red-600"
            />
            <div className="space-y-2.5">
              {urgent.map((item) => (
                <div key={item.product_id} className="bg-white rounded-2xl border border-red-100 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-neutral-900 mb-0.5">{item.name}</p>
                      <p className="text-xs text-neutral-500 mb-2">
                        {item.quantity} {item.unit} · daily use: {item.daily_consumption} {item.unit}
                      </p>
                      <div className="flex items-center gap-3 flex-wrap">
                        <DaysLabel days={item.days_remaining} />
                        <ConfidenceBar value={item.confidence} level={item.confidence_level} />
                      </div>
                    </div>
                    <button
                      onClick={() => handleTakeCareOf(item)}
                      disabled={actionItem === item.product_id}
                      className="shrink-0 px-3.5 py-2 rounded-xl bg-neutral-900 hover:bg-neutral-800 text-white text-xs font-bold flex items-center gap-1.5 transition-all disabled:opacity-60"
                    >
                      {actionItem === item.product_id ? (
                        <><RotateCcw className="w-3.5 h-3.5 animate-spin" /> Working…</>
                      ) : (
                        <><Zap className="w-3.5 h-3.5" /> Take care of it</>
                      )}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* UNCERTAIN */}
        {uncertain.length > 0 && (
          <section className="mb-6">
            <SectionHeader
              icon={<HelpCircle className="w-4 h-4 text-amber-500" />}
              title="Uncertain"
              count={uncertain.length}
              color="text-amber-600"
            />
            <div className="space-y-2.5">
              {uncertain.map((item) => (
                <div key={item.product_id} className="bg-white rounded-2xl border border-amber-100 p-4">
                  <div className="flex items-start gap-4">
                    <div className="flex-1 min-w-0">
                      <p className="font-bold text-neutral-900 mb-0.5">{item.name}</p>
                      <p className="text-xs text-neutral-500 mb-2">
                        {item.quantity} {item.unit} estimated
                      </p>
                      <ConfidenceBar value={item.confidence} level={item.confidence_level} />
                      <p className="text-xs text-amber-700 mt-2">
                        NOVA isn't confident enough to act automatically. Verify your stock.
                      </p>
                    </div>
                    <button
                      onClick={() => handleCopilotSubmit(`How much ${item.name} do I have?`)}
                      className="shrink-0 px-3 py-1.5 rounded-lg border border-amber-200 text-amber-700 text-xs font-bold hover:bg-amber-50 transition-colors"
                    >
                      Verify
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* UPCOMING */}
        {upcoming.length > 0 && (
          <section className="mb-6">
            <SectionHeader
              icon={<Clock className="w-4 h-4 text-amber-500" />}
              title="Coming up"
              count={upcoming.length}
              color="text-amber-600"
            />
            <div className="bg-white rounded-2xl border border-neutral-200 divide-y divide-neutral-100 overflow-hidden">
              {upcoming.map((item) => (
                <div key={item.product_id} className="px-4 py-3.5 flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-amber-400 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-neutral-800 truncate">{item.name}</p>
                    <p className="text-xs text-neutral-400">
                      {item.quantity} {item.unit} · daily use {item.daily_consumption} {item.unit}
                    </p>
                  </div>
                  <div className="text-right shrink-0">
                    <DaysLabel days={item.days_remaining} />
                    <div className="mt-1">
                      <ConfidenceBar value={item.confidence} level="" />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* COMFORTABLE — collapsible */}
        {comfortable.length > 0 && (
          <section>
            <button
              onClick={() => setShowComfortable(!showComfortable)}
              className="flex items-center gap-2 mb-3 w-full text-left"
            >
              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              <span className="text-xs font-bold tracking-widest uppercase text-emerald-600">
                Well stocked
              </span>
              <span className="text-xs font-bold bg-emerald-50 text-emerald-600 rounded-full px-2 py-0.5">
                {comfortable.length}
              </span>
              <span className="ml-auto">
                {showComfortable ? <ChevronUp className="w-4 h-4 text-neutral-400" /> : <ChevronDown className="w-4 h-4 text-neutral-400" />}
              </span>
            </button>
            {showComfortable && (
              <div className="bg-white rounded-2xl border border-neutral-200 divide-y divide-neutral-100 overflow-hidden">
                {comfortable.map((item) => (
                  <div key={item.product_id} className="px-4 py-3 flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-semibold text-neutral-700 truncate">{item.name}</p>
                      <p className="text-xs text-neutral-400">
                        {item.quantity} {item.unit} · {Math.ceil(item.days_remaining)} days
                      </p>
                    </div>
                    <MinusCircle className="w-4 h-4 text-emerald-400 shrink-0" />
                  </div>
                ))}
              </div>
            )}
            {!showComfortable && (
              <p className="text-xs text-neutral-400 ml-6">
                {comfortable.map((i) => i.name.split(" ")[0]).join(", ")} — no action needed.
              </p>
            )}
          </section>
        )}

        {items.length === 0 && (
          <div className="text-center py-12">
            <MinusCircle className="w-8 h-8 text-neutral-300 mx-auto mb-3" />
            <p className="font-bold text-neutral-500">Your pantry is empty.</p>
            <p className="text-sm text-neutral-400">Tell NOVA what you have using the copilot above.</p>
          </div>
        )}
      </div>
    </div>
  );
}
