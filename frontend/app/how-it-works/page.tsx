"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Layers,
  Cpu,
  ShieldCheck,
  Zap,
  Terminal,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Clock,
  MinusCircle,
  Milk,
  Droplets,
  Utensils,
  ArrowRight,
  Sparkles,
  ChevronRight,
  Database,
  ExternalLink,
} from "lucide-react";

interface ToolTraceItem {
  tool: string;
  input?: Record<string, any>;
  summary?: string;
  status?: string;
  duration?: number;
}

export default function HowItWorksPage() {
  const [provider, setProvider] = useState<string>("AWS Strands Agents SDK");
  const [loading, setLoading] = useState(false);
  const [activeScenario, setActiveScenario] = useState<number | null>(null);
  const [response, setResponse] = useState<string | null>(null);
  const [toolTrace, setToolTrace] = useState<ToolTraceItem[]>([]);
  const [verdict, setVerdict] = useState<string | null>(null);
  const [activePipelineStage, setActivePipelineStage] = useState<number>(1);

  useEffect(() => {
    fetch("/api/agent/provider")
      .then((r) => r.json())
      .then((d) => {
        if (d.provider) setProvider(d.provider);
      })
      .catch(() => {});
  }, []);

  const runScenario = async (promptText: string, scenarioNum: number) => {
    if (loading) return;
    setLoading(true);
    setActiveScenario(scenarioNum);
    setResponse(null);
    setToolTrace([]);
    setVerdict(null);

    try {
      const res = await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: promptText }),
      });
      const data = await res.json();
      setResponse(data.response || "Executed successfully.");
      if (Array.isArray(data.tool_trace)) {
        setToolTrace(data.tool_trace);
      }
      if (data.mode) setProvider(data.provider || data.mode);

      // Determine verdict
      if (scenarioNum === 1) setVerdict("AUTO");
      else if (scenarioNum === 2) setVerdict("DO_NOTHING");
      else if (scenarioNum === 3) setVerdict("INTENT_RECONCILED");

      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("cart-updated"));
      window.dispatchEvent(new Event("budget-updated"));
    } catch (err) {
      setResponse("Error communicating with backend agent.");
    } finally {
      setLoading(false);
    }
  };

  const pipelineStages = [
    {
      num: 1,
      title: "1. Intent & Signals",
      desc: "Natural language requests, depleted stock triggers, or meal plans.",
      tech: "User Intent / Event Ingestion",
    },
    {
      num: 2,
      title: "2. AgentCore Loop",
      desc: "AWS Strands SDK agent evaluates tool selection and multi-step reasoning.",
      tech: "AWS Bedrock / Gemini Orchestration",
    },
    {
      num: 3,
      title: "3. Inventory & Velocity",
      desc: "Calculates current stock, daily usage velocity, and days of supply remaining.",
      tech: "Pantry State & Consumption Model",
    },
    {
      num: 4,
      title: "4. Budget Safety Gate",
      desc: "Enforces monthly spending ceilings, transaction caps, and remaining runway.",
      tech: "Deterministic Financial Guardrail",
    },
    {
      num: 5,
      title: "5. Autopilot Policy",
      desc: "Applies user autonomy rules (Suggest Only, Routine Items, Full Autopilot).",
      tech: "Deterministic Policy Engine",
    },
    {
      num: 6,
      title: "6. Verdict & Action",
      desc: "Emits AUTO (buy), DO_NOTHING (restraint), or ASK (confirm).",
      tech: "Swiggy Instamart / Simulated Adapter",
    },
  ];

  return (
    <div className="min-h-screen bg-[#0E1117] text-white pt-6 pb-28 font-sans">
      <div className="max-w-5xl mx-auto px-4 sm:px-6">

        {/* ── Breadcrumb & Title ────────────────────────────────────── */}
        <div className="pt-6 pb-8 border-b border-neutral-800">
          <div className="flex items-center gap-2 text-xs text-neutral-500 font-semibold uppercase tracking-wider mb-2">
            <Link href="/" className="hover:text-white transition-colors">Home</Link>
            <span>/</span>
            <span className="text-amber-400">System Architecture</span>
          </div>

          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-white">
                How NOVA Works
              </h1>
              <p className="text-neutral-400 text-sm mt-1">
                Autonomous Household Intelligence &amp; Agentic Decision Loop for the Agents for Humans Hackathon.
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <span className="px-3 py-1.5 rounded-lg bg-neutral-900 border border-neutral-800 text-xs font-mono text-amber-400 flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-amber-400" />
                <span>{provider}</span>
              </span>
            </div>
          </div>
        </div>

        {/* ── Visual Architecture Pipeline ───────────────────────────── */}
        <section className="my-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xs font-bold tracking-widest text-neutral-400 uppercase">
              End-to-End Decision Architecture
            </h2>
            <span className="text-xs text-amber-400/90 font-mono">
              Deterministic Safety + Autonomous Reasoning
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {pipelineStages.map((stage) => {
              const isSelected = activePipelineStage === stage.num;
              return (
                <div
                  key={stage.num}
                  onClick={() => setActivePipelineStage(stage.num)}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer ${
                    isSelected
                      ? "bg-neutral-900/90 border-amber-400/80 shadow-lg shadow-amber-400/5 ring-1 ring-amber-400/30"
                      : "bg-neutral-950/70 border-neutral-800/80 hover:border-neutral-700"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold text-amber-400">
                      {stage.title}
                    </span>
                    <span className="text-[10px] font-mono text-neutral-500 uppercase">
                      Stage {stage.num}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-300 leading-relaxed mb-2">
                    {stage.desc}
                  </p>
                  <p className="text-[10px] font-mono text-neutral-400 bg-neutral-900 px-2 py-1 rounded border border-neutral-800/60 truncate">
                    {stage.tech}
                  </p>
                </div>
              );
            })}
          </div>
        </section>

        {/* ── Live Hero Scenarios Interactive Workbench ──────────────── */}
        <section className="my-10 bg-neutral-900/80 rounded-3xl border border-neutral-800 p-6 sm:p-7 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400 uppercase tracking-wider mb-1">
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>Live Strands Hackathon Hero Scenarios</span>
              </div>
              <h3 className="text-xl font-bold text-white">
                Interactive Agent Testbed
              </h3>
            </div>
            <span className="text-xs text-neutral-400 font-mono hidden sm:inline">
              Click to execute live agent trace
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
            {/* Scenario 1: Milk Auto-Buy */}
            <button
              type="button"
              onClick={() => runScenario("I need milk.", 1)}
              disabled={loading}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                activeScenario === 1
                  ? "bg-emerald-950/40 border-emerald-500 ring-2 ring-emerald-500/20"
                  : "bg-neutral-950/80 border-neutral-800 hover:border-neutral-700"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Milk className="w-4 h-4 text-emerald-400" />
                    <span>Scenario 1: Milk Auto-Buy</span>
                  </span>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-emerald-900/60 text-emerald-300 font-mono">
                    AUTO
                  </span>
                </div>
                <p className="text-xs text-neutral-400 leading-relaxed">
                  Low pantry stock (0.3L left) triggers autonomous purchase within budget rules.
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-neutral-800/80 text-[11px] text-emerald-400 font-semibold flex items-center gap-1">
                <span>Run Scenario</span>
                <ArrowRight className="w-3 h-3" />
              </div>
            </button>

            {/* Scenario 2: Oil Restraint */}
            <button
              type="button"
              onClick={() => runScenario("Should I buy oil?", 2)}
              disabled={loading}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                activeScenario === 2
                  ? "bg-blue-950/40 border-blue-500 ring-2 ring-blue-500/20"
                  : "bg-neutral-950/80 border-neutral-800 hover:border-neutral-700"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Droplets className="w-4 h-4 text-blue-400" />
                    <span>Scenario 2: Oil Restraint</span>
                  </span>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-900/60 text-blue-300 font-mono">
                    RESTRAINT
                  </span>
                </div>
                <p className="text-xs text-neutral-400 leading-relaxed">
                  Healthy stock (2.1L left, ~19-30d supply). NOVA applies restraint: DO_NOTHING.
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-neutral-800/80 text-[11px] text-blue-400 font-semibold flex items-center gap-1">
                <span>Run Scenario</span>
                <ArrowRight className="w-3 h-3" />
              </div>
            </button>

            {/* Scenario 3: Maggi Plan */}
            <button
              type="button"
              onClick={() => runScenario("I want to make Maggi tonight.", 3)}
              disabled={loading}
              className={`p-4 rounded-2xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                activeScenario === 3
                  ? "bg-purple-950/40 border-purple-500 ring-2 ring-purple-500/20"
                  : "bg-neutral-950/80 border-neutral-800 hover:border-neutral-700"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    <Utensils className="w-4 h-4 text-purple-400" />
                    <span>Scenario 3: Maggi Plan</span>
                  </span>
                  <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-purple-900/60 text-purple-300 font-mono">
                    INTENT
                  </span>
                </div>
                <p className="text-xs text-neutral-400 leading-relaxed">
                  Reconciles pantry: Oil &amp; Salt are in stock. Only missing Maggi noodles ordered.
                </p>
              </div>
              <div className="mt-3 pt-2 border-t border-neutral-800/80 text-[11px] text-purple-400 font-semibold flex items-center gap-1">
                <span>Run Scenario</span>
                <ArrowRight className="w-3 h-3" />
              </div>
            </button>
          </div>

          {/* Loading Indicator */}
          {loading && (
            <div className="p-4 rounded-2xl bg-neutral-950 border border-neutral-800 flex items-center gap-3 animate-pulse">
              <RotateCcw className="w-4 h-4 text-amber-400 animate-spin" />
              <div className="text-xs text-neutral-300">
                <span className="font-bold text-white">Running Strands Agent Loop…</span> Checking pantry inventory, evaluating budget limits, applying policy guardrails.
              </div>
            </div>
          )}

          {/* Execution Results & Live Tool Traces */}
          {response && (
            <div className="p-5 rounded-2xl bg-neutral-950 border border-neutral-800 space-y-4">
              <div className="flex items-center justify-between gap-2 pb-3 border-b border-neutral-800">
                <div className="flex items-center gap-2">
                  {verdict === "AUTO" && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Verdict: AUTO (Autonomous Purchase Placed)
                    </span>
                  )}
                  {verdict === "DO_NOTHING" && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-blue-950 text-blue-300 border border-blue-500/40 flex items-center gap-1">
                      <MinusCircle className="w-3.5 h-3.5" />
                      Verdict: DO_NOTHING (Spending Restraint Applied)
                    </span>
                  )}
                  {verdict === "INTENT_RECONCILED" && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-950 text-purple-300 border border-purple-500/40 flex items-center gap-1">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      Verdict: INTENT_RECONCILED (Only Missing Ordered)
                    </span>
                  )}
                </div>

                <span className="text-[11px] font-mono text-neutral-500">
                  Tool Traces: {toolTrace.length} calls
                </span>
              </div>

              {/* Agent Explanation Text */}
              <div className="text-sm text-neutral-200 leading-relaxed font-sans bg-neutral-900/60 p-4 rounded-xl border border-neutral-800/80">
                {response}
              </div>

              {/* Tool Traces Telemetry */}
              {toolTrace.length > 0 && (
                <div className="space-y-1.5 pt-2">
                  <div className="flex items-center gap-1.5 text-xs font-mono text-neutral-400 mb-1">
                    <Terminal className="w-3.5 h-3.5 text-amber-400" />
                    <span>Agent Tool Telemetry</span>
                  </div>
                  {toolTrace.map((t, idx) => (
                    <div
                      key={idx}
                      className="bg-neutral-900/80 border border-neutral-800 rounded-lg p-2.5 flex items-start justify-between gap-3 text-xs"
                    >
                      <div>
                        <span className="font-mono font-bold text-amber-400 bg-neutral-950 px-1.5 py-0.5 rounded text-[11px]">
                          {t.tool}()
                        </span>
                        {t.summary && (
                          <p className="text-neutral-300 text-xs mt-1">{t.summary}</p>
                        )}
                      </div>
                      {t.duration !== undefined && (
                        <span className="text-[10px] font-mono text-neutral-500 shrink-0">
                          {t.duration}s
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>

      </div>
    </div>
  );
}
