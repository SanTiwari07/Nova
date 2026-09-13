"use client";

import { useState, useEffect } from "react";
import {
  Sparkles,
  Send,
  CheckCircle2,
  AlertCircle,
  Clock,
  ShieldCheck,
  RotateCcw,
  ChevronDown,
  ChevronUp,
  Terminal,
  Cpu,
  Layers,
  ArrowRight,
} from "lucide-react";

interface ToolTraceItem {
  tool: string;
  input?: Record<string, any>;
  summary?: string;
  status?: string;
  duration?: number;
}

interface CommandBoxProps {
  onScenarioDispatched?: (scenarioNum?: number) => void;
  className?: string;
  compact?: boolean;
  id?: string;
}

export default function CommandBox({
  onScenarioDispatched,
  className = "",
  compact = false,
  id = "today-command-box",
}: CommandBoxProps) {
  const [command, setCommand] = useState("");
  const [response, setResponse] = useState("");
  const [mode, setMode] = useState<string>("");
  const [provider, setProvider] = useState<string>("");
  const [toolTrace, setToolTrace] = useState<ToolTraceItem[]>([]);
  const [decisionVerdict, setDecisionVerdict] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  // Check agent provider on mount
  useEffect(() => {
    fetch("/api/agent/provider")
      .then((res) => res.json())
      .then((data) => {
        if (data.provider) setProvider(data.provider);
      })
      .catch(() => {});
  }, []);

  // Listen for custom trigger events from other components
  useEffect(() => {
    const handleRunScenario = (e: any) => {
      if (e?.detail?.prompt) {
        runPrompt(e.detail.prompt, e.detail.scenarioNum);
      }
    };
    window.addEventListener("nova-run-scenario", handleRunScenario);
    return () => window.removeEventListener("nova-run-scenario", handleRunScenario);
  }, []);

  const runPrompt = async (promptText: string, scenarioNum?: number) => {
    if (loading || !promptText.trim()) return;
    setLoading(true);
    setCommand(promptText);
    setResponse("");
    setToolTrace([]);
    setMode("");
    setDecisionVerdict(null);

    try {
      const res = await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: promptText }),
      });
      const data = await res.json();
      const respText = data.response || "Executed successfully.";
      setResponse(respText);
      setMode(data.mode || "STRANDS_AGENT");
      if (data.provider) setProvider(data.provider);

      if (Array.isArray(data.tool_trace)) {
        setToolTrace(data.tool_trace);
        for (const t of data.tool_trace) {
          if (t.summary && t.summary.includes("Verdict: AUTO")) setDecisionVerdict("AUTO");
          else if (t.summary && t.summary.includes("Verdict: DO_NOTHING")) setDecisionVerdict("DO_NOTHING");
          else if (t.summary && t.summary.includes("Verdict: ASK")) setDecisionVerdict("ASK");
          else if (t.summary && t.summary.includes("Verdict: BLOCKED")) setDecisionVerdict("BLOCKED");
          else if (t.summary && t.summary.includes("Verdict: WAIT")) setDecisionVerdict("WAIT");
          else if (t.tool === "record_restraint_decision") setDecisionVerdict("DO_NOTHING");
        }
      }

      if (!decisionVerdict) {
        if (respText.includes("AUTO")) setDecisionVerdict("AUTO");
        else if (respText.includes("DO_NOTHING") || respText.includes("Restraint")) setDecisionVerdict("DO_NOTHING");
        else if (respText.includes("ASK") || respText.includes("confirmation")) setDecisionVerdict("ASK");
        else if (respText.includes("BLOCKED")) setDecisionVerdict("BLOCKED");
      }

      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("cart-updated"));
      window.dispatchEvent(new Event("budget-updated"));
      if (onScenarioDispatched) {
        onScenarioDispatched(scenarioNum);
      }
    } catch (err) {
      setResponse("NOVA is momentarily unavailable. Please check your connection.");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;
    runPrompt(command);
  };

  const samplePrompts = [
    "I want to make Maggi tonight",
    "Do I need milk?",
    "What's running low?",
    "Why did you buy oil?",
  ];

  return (
    <div id={id} className={`w-full ${className}`}>
      <div className="bg-white rounded-3xl border border-neutral-200/90 shadow-sm p-6 sm:p-7">
        
        {/* Title */}
        <div className="mb-4">
          <h3 className="text-xl font-bold text-neutral-950 tracking-tight">
            What can I take care of?
          </h3>
          <p className="text-neutral-500 text-xs mt-0.5">
            Ask about your pantry, plan a meal, or let NOVA take care of routine restocks.
          </p>
        </div>

        {/* Natural Language Prompt Input */}
        <form onSubmit={handleSubmit} className="relative mb-3">
          <div className="relative rounded-2xl border border-neutral-300 focus-within:border-neutral-900 focus-within:ring-2 focus-within:ring-neutral-900/10 transition-all bg-white shadow-inner overflow-hidden">
            <textarea
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  if (command.trim() && !loading) runPrompt(command);
                }
              }}
              rows={compact ? 2 : 3}
              placeholder="Tell NOVA what you need..."
              disabled={loading}
              className="w-full px-4 pt-3.5 pb-12 text-sm text-neutral-900 placeholder:text-neutral-400 outline-none resize-none bg-transparent"
            />
            
            <div className="absolute right-3 bottom-3 flex items-center gap-2">
              <button
                type="submit"
                disabled={loading || !command.trim()}
                className="px-4 py-2 rounded-xl bg-neutral-950 hover:bg-neutral-800 disabled:opacity-40 text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-sm cursor-pointer"
              >
                {loading ? (
                  <>
                    <RotateCcw className="w-3.5 h-3.5 animate-spin" />
                    <span>Thinking…</span>
                  </>
                ) : (
                  <>
                    <span>Send</span>
                    <Send className="w-3.5 h-3.5" />
                  </>
                )}
              </button>
            </div>
          </div>
        </form>

        {/* Suggestion Chips */}
        <div className="flex items-center gap-1.5 flex-wrap text-xs text-neutral-500">
          <span className="font-semibold text-neutral-400 mr-1">Try:</span>
          {samplePrompts.map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => runPrompt(p)}
              disabled={loading}
              className="px-3 py-1.5 rounded-full bg-neutral-100 hover:bg-neutral-200 text-neutral-700 text-xs font-medium transition-colors cursor-pointer"
            >
              &ldquo;{p}&rdquo;
            </button>
          ))}
        </div>

        {/* Response Presentation */}
        {response && (
          <div className="mt-5 bg-[#F9F9F8] border border-neutral-200 rounded-2xl p-5 shadow-xs transition-all">
            {/* Status / Verdict Badge */}
            <div className="flex items-center justify-between gap-2 mb-3 pb-3 border-b border-neutral-200/80">
              <div className="flex items-center gap-2">
                {decisionVerdict === "AUTO" && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                    Done for you
                  </span>
                )}
                {decisionVerdict === "DO_NOTHING" && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-800">
                    <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
                    All sorted · No action needed
                  </span>
                )}
                {decisionVerdict === "ASK" && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-800">
                    <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
                    Needs your input
                  </span>
                )}
                {!decisionVerdict && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-neutral-200 text-neutral-800">
                    <Sparkles className="w-3.5 h-3.5 text-neutral-600" />
                    Assistant
                  </span>
                )}
              </div>

              {/* Technical details toggle for judges / dev mode */}
              <button
                type="button"
                onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
                className="text-xs text-neutral-400 hover:text-neutral-700 flex items-center gap-1 transition-colors"
              >
                <span>{showTechnicalDetails ? "Hide technical details" : "Technical details"}</span>
                {showTechnicalDetails ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
              </button>
            </div>

            {/* Conversational Assistant Explanation */}
            <div className="text-sm text-neutral-800 leading-relaxed font-sans whitespace-pre-wrap">
              {response}
            </div>

            {/* Optional Technical Details for Judges & Architecture Review */}
            {showTechnicalDetails && (
              <div className="mt-4 pt-3.5 border-t border-neutral-200 text-xs">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5 font-bold text-neutral-700">
                    <Terminal className="w-3.5 h-3.5 text-amber-600" />
                    <span>Agent Telemetry &amp; Tool Traces ({toolTrace.length})</span>
                  </div>
                  {provider && (
                    <span className="text-[10px] font-mono bg-neutral-200 text-neutral-700 px-2 py-0.5 rounded">
                      {provider}
                    </span>
                  )}
                </div>

                {toolTrace.length > 0 ? (
                  <div className="space-y-1.5">
                    {toolTrace.map((t, idx) => (
                      <div
                        key={idx}
                        className="bg-white border border-neutral-200 rounded-lg p-2.5 flex items-start justify-between gap-2"
                      >
                        <div>
                          <span className="font-mono font-bold text-neutral-900 bg-neutral-100 px-1.5 py-0.5 rounded text-[11px]">
                            {t.tool}()
                          </span>
                          {t.summary && (
                            <p className="text-neutral-600 text-xs mt-1">{t.summary}</p>
                          )}
                        </div>
                        {t.duration !== undefined && (
                          <span className="text-[10px] font-mono text-neutral-400 shrink-0">
                            {t.duration}s
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-neutral-500 text-[11px]">
                    Direct intent reconciliation without separate tool invocations.
                  </p>
                )}
              </div>
            )}

          </div>
        )}

      </div>
    </div>
  );
}
