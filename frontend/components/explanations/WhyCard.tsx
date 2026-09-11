import { useState } from "react";

interface WhyCardProps {
  decision: {
    type: string;
    confidence: number;
    reasoning: string[];
    inventoryState?: string;
    depletionEstimate?: string;
    product?: { name: string; price: number };
  };
}

export default function WhyCard({ decision }: WhyCardProps) {
  const [open, setOpen] = useState(false);

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="text-xs font-semibold text-[#FF9900] hover:underline"
      >
        {open ? "Hide reasoning" : "Why?"}
      </button>
      {open && (
        <div className="mt-2 p-4 bg-orange-50 rounded-xl border border-orange-100">
          <p className="text-xs font-bold text-orange-900 mb-2">NOVA reasoning</p>
          <ul className="space-y-1">
            {decision.reasoning.map((r, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-orange-400 mt-0.5 shrink-0">•</span>
                <p className="text-xs text-neutral-700">{r}</p>
              </li>
            ))}
          </ul>
          <div className="mt-3 flex items-center gap-4 pt-3 border-t border-orange-100">
            <div>
              <p className="text-xs text-neutral-400">Confidence</p>
              <p className="text-sm font-bold text-neutral-900">{decision.confidence}%</p>
            </div>
            {decision.inventoryState && (
              <div>
                <p className="text-xs text-neutral-400">Inventory</p>
                <p className="text-sm font-bold text-neutral-900">{decision.inventoryState}</p>
              </div>
            )}
            {decision.depletionEstimate && (
              <div>
                <p className="text-xs text-neutral-400">Runs out</p>
                <p className="text-sm font-bold text-neutral-900">{decision.depletionEstimate}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
