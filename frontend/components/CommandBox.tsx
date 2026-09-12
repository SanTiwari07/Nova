import { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Terminal, 
  ShieldCheck, 
  CheckCircle2, 
  ArrowRight, 
  AlertCircle, 
  Clock, 
  ShieldAlert, 
  RefreshCw,
  Cpu,
  Layers
} from 'lucide-react';

interface ToolTraceItem {
  tool: string;
  input?: Record<string, any>;
  summary?: string;
  status?: string;
  duration?: number;
}

interface CommandBoxProps {
  onScenarioDispatched?: (scenarioNum: number) => void;
  className?: string;
}

export default function CommandBox({ onScenarioDispatched, className = "" }: CommandBoxProps) {
  const [command, setCommand] = useState('');
  const [response, setResponse] = useState('');
  const [mode, setMode] = useState<string>('');
  const [provider, setProvider] = useState<string>('');
  const [toolTrace, setToolTrace] = useState<ToolTraceItem[]>([]);
  const [decisionVerdict, setDecisionVerdict] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeScenario, setActiveScenario] = useState<number | null>(null);

  // Check agent provider on mount
  useEffect(() => {
    fetch('/api/agent/provider')
      .then(res => res.json())
      .then(data => {
        if (data.provider) setProvider(data.provider);
      })
      .catch(() => {});
  }, []);

  // Listen for custom trigger events from other components
  useEffect(() => {
    const handleRunScenario = (e: any) => {
      if (e?.detail?.prompt) {
        runCommand(e.detail.prompt, e.detail.scenarioNum);
      }
    };
    window.addEventListener('nova-run-scenario', handleRunScenario);
    return () => window.removeEventListener('nova-run-scenario', handleRunScenario);
  }, []);

  const runCommand = async (promptText: string, scenarioNum?: number) => {
    if (loading || !promptText.trim()) return;
    setLoading(true);
    setCommand(promptText);
    setResponse('');
    setToolTrace([]);
    setMode('');
    setDecisionVerdict(null);
    if (scenarioNum !== undefined) setActiveScenario(scenarioNum);

    try {
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: promptText })
      });
      const data = await res.json();
      const respText = data.response || 'Executed successfully.';
      setResponse(respText);
      setMode(data.mode || 'STRANDS_AGENT');
      if (data.provider) setProvider(data.provider);

      if (Array.isArray(data.tool_trace)) {
        setToolTrace(data.tool_trace);
        
        // Extract decision verdict from tool traces or response
        for (const t of data.tool_trace) {
          if (t.summary && t.summary.includes('Verdict: AUTO')) setDecisionVerdict('AUTO');
          else if (t.summary && t.summary.includes('Verdict: DO_NOTHING')) setDecisionVerdict('DO_NOTHING');
          else if (t.summary && t.summary.includes('Verdict: ASK')) setDecisionVerdict('ASK');
          else if (t.summary && t.summary.includes('Verdict: BLOCKED')) setDecisionVerdict('BLOCKED');
          else if (t.summary && t.summary.includes('Verdict: WAIT')) setDecisionVerdict('WAIT');
          else if (t.tool === 'record_restraint_decision') setDecisionVerdict('DO_NOTHING');
        }
      }

      if (!decisionVerdict) {
        if (respText.includes('AUTO')) setDecisionVerdict('AUTO');
        else if (respText.includes('DO_NOTHING') || respText.includes('Restraint')) setDecisionVerdict('DO_NOTHING');
        else if (respText.includes('ASK') || respText.includes('confirmation')) setDecisionVerdict('ASK');
        else if (respText.includes('BLOCKED')) setDecisionVerdict('BLOCKED');
      }

      // Notify other views that household state changed (pantry, budget, cart)
      window.dispatchEvent(new Event('household-updated'));
      window.dispatchEvent(new Event('cart-updated'));
      if (onScenarioDispatched && scenarioNum !== undefined) {
        onScenarioDispatched(scenarioNum);
      }
    } catch (err) {
      setResponse('Error communicating with NOVA Strands agent backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;
    runCommand(command);
  };

  const getVerdictBadge = () => {
    switch (decisionVerdict) {
      case 'AUTO':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-emerald-50 text-emerald-800 border border-emerald-300 rounded-full text-xs font-bold uppercase tracking-wider">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            Decision: AUTO (Autonomous Action Authorized)
          </span>
        );
      case 'DO_NOTHING':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-blue-50 text-blue-800 border border-blue-300 rounded-full text-xs font-bold uppercase tracking-wider">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-600" />
            Decision: DO_NOTHING (Restraint Applied · Stock Healthy)
          </span>
        );
      case 'ASK':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-amber-50 text-amber-800 border border-amber-300 rounded-full text-xs font-bold uppercase tracking-wider">
            <AlertCircle className="w-3.5 h-3.5 text-amber-600" />
            Decision: ASK (Human Confirmation Required)
          </span>
        );
      case 'WAIT':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-purple-50 text-purple-800 border border-purple-300 rounded-full text-xs font-bold uppercase tracking-wider">
            <Clock className="w-3.5 h-3.5 text-purple-600" />
            Decision: WAIT (Price Signal Deferred)
          </span>
        );
      case 'BLOCKED':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 bg-rose-50 text-rose-800 border border-rose-300 rounded-full text-xs font-bold uppercase tracking-wider">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
            Decision: BLOCKED (Policy Restriction Enforced)
          </span>
        );
      default:
        return null;
    }
  };

  const getProviderBadge = () => {
    const p = provider || mode;
    if (p.includes('BEDROCK')) {
      return (
        <span className="flex items-center gap-1 text-[11px] bg-[#232F3E] text-[#FF9900] px-2.5 py-1 rounded-md font-mono font-medium border border-[#FF9900]/30 shadow-xs">
          <Cpu className="w-3 h-3 text-[#FF9900]" />
          AWS Bedrock (Claude 3.5)
        </span>
      );
    }
    if (p.includes('GEMINI')) {
      return (
        <span className="flex items-center gap-1 text-[11px] bg-neutral-900 text-blue-400 px-2.5 py-1 rounded-md font-mono font-medium border border-blue-500/30 shadow-xs">
          <Sparkles className="w-3 h-3 text-blue-400" />
          Google Gemini (2.5 Flash)
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 text-[11px] bg-neutral-100 text-neutral-700 px-2.5 py-1 rounded-md font-mono font-medium border border-neutral-300">
        <Layers className="w-3 h-3 text-neutral-500" />
        Strands Tools Engine
      </span>
    );
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Console Card */}
      <div className="bg-white border border-neutral-200/90 rounded-2xl shadow-sm p-4 md:p-6 transition-all hover:border-neutral-300">
        
        {/* Header Bar */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-4 pb-3 border-b border-neutral-100">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#FF9900] text-white flex items-center justify-center font-bold text-sm shadow-xs">
              N
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-neutral-900 text-base">NOVA Autonomous Copilot</span>
                <span className="px-2 py-0.5 bg-orange-50 border border-orange-200 text-orange-800 text-[10px] font-bold rounded-full uppercase tracking-wider">
                  AWS Strands SDK
                </span>
              </div>
              <p className="text-xs text-neutral-500">
                Confidence-aware household decision autopilot &middot; Zero-cost simulated commerce
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {getProviderBadge()}
          </div>
        </div>

        {/* 1-Click Hero Scenario Buttons */}
        <div className="mb-4">
          <div className="text-[11px] font-bold text-neutral-500 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3 h-3 text-[#FF9900]" />
            Live Strands Hackathon Hero Scenarios (Click to Execute):
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
            <button
              type="button"
              onClick={() => runCommand("I need milk.", 1)}
              disabled={loading}
              className={`text-left p-3 rounded-xl border text-xs transition-all flex flex-col justify-between ${
                activeScenario === 1
                  ? "bg-emerald-50/80 border-emerald-400 ring-2 ring-emerald-400/20 shadow-xs"
                  : "bg-neutral-50 hover:bg-neutral-100/80 border-neutral-200"
              }`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <span className="font-bold text-neutral-900 flex items-center gap-1.5">
                  <span>🥛</span> Scenario 1: Milk Auto-Buy
                </span>
                <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.2 rounded font-semibold">
                  AUTO
                </span>
              </div>
              <p className="text-[11px] text-neutral-600 line-clamp-1">
                Low pantry stock (0.3L) &rarr; Search &rarr; Auto-order
              </p>
            </button>

            <button
              type="button"
              onClick={() => runCommand("Should I buy oil?", 2)}
              disabled={loading}
              className={`text-left p-3 rounded-xl border text-xs transition-all flex flex-col justify-between ${
                activeScenario === 2
                  ? "bg-blue-50/80 border-blue-400 ring-2 ring-blue-400/20 shadow-xs"
                  : "bg-neutral-50 hover:bg-neutral-100/80 border-neutral-200"
              }`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <span className="font-bold text-neutral-900 flex items-center gap-1.5">
                  <span>🛢️</span> Scenario 2: Oil Restraint
                </span>
                <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.2 rounded font-semibold">
                  RESTRAINT
                </span>
              </div>
              <p className="text-[11px] text-neutral-600 line-clamp-1">
                2.1L in stock (~30 days left) &rarr; DO_NOTHING
              </p>
            </button>

            <button
              type="button"
              onClick={() => runCommand("I want to make Maggi tonight.", 3)}
              disabled={loading}
              className={`text-left p-3 rounded-xl border text-xs transition-all flex flex-col justify-between ${
                activeScenario === 3
                  ? "bg-purple-50/80 border-purple-400 ring-2 ring-purple-400/20 shadow-xs"
                  : "bg-neutral-50 hover:bg-neutral-100/80 border-neutral-200"
              }`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <span className="font-bold text-neutral-900 flex items-center gap-1.5">
                  <span>🍜</span> Scenario 3: Maggi Reconciliation
                </span>
                <span className="text-[10px] bg-purple-100 text-purple-800 px-1.5 py-0.2 rounded font-semibold">
                  INTENT
                </span>
              </div>
              <p className="text-[11px] text-neutral-600 line-clamp-1">
                Reconcile: Oil/Salt in pantry &rarr; Order noodles only
              </p>
            </button>
          </div>
        </div>

        {/* Natural Language Prompt Input */}
        <form onSubmit={handleSubmit} className="relative group">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Sparkles className="text-[#FF9900] w-4 h-4" />
          </div>
          <input 
            type="text" 
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            placeholder="Type or click a scenario: 'I need milk', 'Should I buy oil?', 'What is running low?'..."
            disabled={loading}
            className="w-full pl-11 pr-32 py-3.5 rounded-xl bg-neutral-50 border border-neutral-200 text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent transition-all placeholder:text-neutral-400"
          />
          <div className="absolute inset-y-0 right-0 pr-2 flex items-center">
            <button 
              type="submit" 
              disabled={loading || !command.trim()}
              className="px-4 py-2 bg-neutral-900 text-white rounded-lg hover:bg-neutral-800 disabled:opacity-50 text-xs font-semibold transition-colors flex items-center gap-1.5 shadow-xs"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Reasoning...</span>
                </>
              ) : (
                <>
                  <span>Dispatch</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </form>

        {/* Loading State */}
        {loading && (
          <div className="mt-4 bg-orange-50/50 border border-orange-200/60 rounded-xl p-3.5 flex items-center gap-3 text-neutral-700 text-xs animate-pulse">
            <div className="w-2.5 h-2.5 rounded-full bg-[#FF9900] animate-ping" />
            <div className="flex flex-col">
              <span className="font-semibold text-neutral-900">
                Strands Agent Loop Running ({provider || "AWS Strands Agents SDK"})
              </span>
              <span className="text-[11px] text-neutral-500">
                Inspecting pantry &middot; Checking budget limits &middot; Running deterministic safety gates...
              </span>
            </div>
          </div>
        )}

        {/* Results Presentation */}
        {response && (
          <div className="mt-5 bg-gradient-to-b from-neutral-50 to-orange-50/20 border border-neutral-200 rounded-xl p-5 shadow-xs relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1.5 h-full bg-[#FF9900]"></div>

            {/* Verdict and Status Header */}
            <div className="flex flex-wrap items-center justify-between gap-2 mb-3 pb-2.5 border-b border-neutral-200/70">
              <div className="flex items-center gap-2">
                {getVerdictBadge()}
              </div>

              <div className="flex items-center gap-1.5 text-[11px] text-neutral-500 font-mono">
                <span>Traces: {toolTrace.length} tools executed</span>
              </div>
            </div>

            {/* Real Strands Tool Traces */}
            {toolTrace.length > 0 && (
              <div className="mb-4 bg-white border border-neutral-200 rounded-lg p-3 text-xs">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-1.5 text-neutral-700 font-semibold text-[11px]">
                    <Terminal className="w-3.5 h-3.5 text-[#FF9900]" />
                    <span>AWS Strands Tool Execution Telemetry:</span>
                  </div>
                  <span className="text-[10px] text-neutral-400 font-mono">
                    Deterministic Guardrails Active
                  </span>
                </div>
                <div className="space-y-1.5">
                  {toolTrace.map((t, idx) => (
                    <div 
                      key={idx} 
                      className="flex items-start justify-between bg-neutral-50/80 rounded p-2 border border-neutral-100 text-[11px]"
                    >
                      <div className="flex items-start gap-2">
                        <span className="font-mono text-neutral-900 font-bold bg-neutral-200/70 px-1.5 py-0.5 rounded text-[10px]">
                          {t.tool}()
                        </span>
                        {t.summary && (
                          <span className="text-neutral-700 mt-0.5">{t.summary}</span>
                        )}
                      </div>
                      {t.duration !== undefined && (
                        <span className="text-[10px] text-neutral-400 font-mono shrink-0 ml-2">
                          {t.duration}s
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Final Agent Explanation */}
            <div className="text-sm text-neutral-800 leading-relaxed whitespace-pre-wrap font-sans bg-white/70 p-3.5 rounded-lg border border-neutral-100">
              {response}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
