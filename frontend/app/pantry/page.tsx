"use client";

import { useState, useEffect } from 'react';

interface PantryItem {
  product_id: string;
  name: string;
  quantity: number;
  unit: string;
  days_remaining: number;
  status: string;
  category: string;
  confidence?: number;
  confidence_score?: string;
}

export default function PantryPage() {
  const [items, setItems] = useState<PantryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [copilotQuery, setCopilotQuery] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentFeedback, setAgentFeedback] = useState<string | null>(null);

  const fetchPantry = () => {
    fetch('/api/pantry')
      .then(res => res.json())
      .then(data => setItems(data))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchPantry();
  }, []);

  const handleCopilotSubmit = async (queryToRun?: string) => {
    const query = queryToRun || copilotQuery;
    if (!query.trim()) return;
    setIsProcessing(true);
    setAgentFeedback(null);
    try {
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: query.trim(), command: query.trim() }),
      });
      const data = await res.json();
      setAgentFeedback(data.response || "Pantry updated.");
      setCopilotQuery("");
      fetchPantry();
    } catch (err) {
      console.error(err);
      setAgentFeedback("Error contacting NOVA Agent.");
    } finally {
      setIsProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="w-12 h-12 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans pb-24">
      <div className="max-w-5xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-extrabold text-neutral-900 mb-2 uppercase tracking-tight">Household Inventory</h1>
          <p className="text-neutral-500 font-medium">Tracking {items.length} essential items in your household with real-time autonomous intelligence.</p>
        </header>

        {/* Agentic Pantry Copilot */}
        <div className="bg-white rounded-3xl p-6 shadow-sm border border-neutral-200 mb-8">
          <div className="flex items-center gap-2 mb-3">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <p className="text-xs font-bold uppercase tracking-wider text-neutral-500">NOVA Pantry Copilot · Real Strands Agent</p>
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleCopilotSubmit();
            }}
            className="flex flex-col md:flex-row gap-3"
          >
            <input
              type="text"
              placeholder="Tell NOVA to update pantry (e.g. 'We ran out of tea', 'Add 2L of milk', 'Check if we need oil')..."
              value={copilotQuery}
              onChange={(e) => setCopilotQuery(e.target.value)}
              disabled={isProcessing}
              className="flex-1 px-4 py-3 bg-neutral-50 border border-neutral-200 rounded-2xl text-sm focus:outline-none focus:border-neutral-900 transition-colors"
            />
            <button
              type="submit"
              disabled={isProcessing || !copilotQuery.trim()}
              className="px-6 py-3 bg-neutral-900 text-white font-bold text-sm rounded-2xl hover:bg-neutral-800 transition-colors disabled:opacity-50 shrink-0"
            >
              {isProcessing ? "NOVA Thinking..." : "Send to Agent"}
            </button>
          </form>

          {/* Quick chip triggers */}
          <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-neutral-100">
            <span className="text-xs text-neutral-400 font-medium self-center">Try asking:</span>
            {[
              "We ran out of tea",
              "Add 2 packets of poha",
              "Check if we need oil",
              "Ran out of salt",
            ].map((chip) => (
              <button
                key={chip}
                type="button"
                onClick={() => handleCopilotSubmit(chip)}
                disabled={isProcessing}
                className="px-3 py-1 bg-neutral-100 hover:bg-neutral-200 text-neutral-700 text-xs font-semibold rounded-lg transition-colors"
              >
                {chip} &rarr;
              </button>
            ))}
          </div>

          {agentFeedback && (
            <div className="mt-4 p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-sm text-emerald-900 leading-relaxed">
              <span className="font-bold block mb-1 text-emerald-950">Agent Decision:</span>
              {agentFeedback}
            </div>
          )}
        </div>
        
        <div className="bg-white rounded-3xl shadow-sm border border-neutral-200 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-neutral-50 border-b border-neutral-200">
              <tr>
                <th className="px-6 py-5 font-bold text-neutral-500 uppercase tracking-wider text-xs">Product</th>
                <th className="px-6 py-5 font-bold text-neutral-500 uppercase tracking-wider text-xs">Estimated Quantity</th>
                <th className="px-6 py-5 font-bold text-neutral-500 uppercase tracking-wider text-xs">Days Remaining</th>
                <th className="px-6 py-5 font-bold text-neutral-500 uppercase tracking-wider text-xs text-right">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100">
              {items.map(item => (
                <tr key={item.product_id} className="hover:bg-neutral-50 transition-colors">
                  <td className="px-6 py-5">
                    <div className="font-bold text-neutral-900 text-sm mb-1">{item.name}</div>
                    <div className="text-xs font-semibold text-neutral-500 uppercase tracking-wider">{item.category}</div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="font-bold text-neutral-900 text-lg">{item.quantity} <span className="text-sm font-medium text-neutral-500">{item.unit}</span></div>
                    {item.status === 'LOW' && (
                       <span className="inline-flex mt-1 items-center px-2 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700 uppercase tracking-wider">
                         Attention Needed
                       </span>
                    )}
                  </td>
                  <td className="px-6 py-5">
                    <div className={`font-bold ${item.days_remaining < 3 ? 'text-red-600' : 'text-neutral-900'}`}>
                      {item.days_remaining} days
                    </div>
                  </td>
                  <td className="px-6 py-5 text-right">
                    <div className={`font-bold text-lg ${(item.confidence ?? 0.88) >= 0.9 ? 'text-green-600' : 'text-neutral-900'}`}>
                      {item.confidence_score || (item.confidence ? `${Math.round(item.confidence * 100)}%` : '88%')}
                    </div>
                    <div className="text-xs text-neutral-500 font-medium uppercase tracking-wider">
                      {(item.confidence ?? 0.88) >= 0.9 ? 'High' : (item.confidence ?? 0.88) >= 0.75 ? 'Moderate' : 'Low'}
                    </div>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-12 text-center text-neutral-500 font-medium">
                    Your inventory tracking is currently empty.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
