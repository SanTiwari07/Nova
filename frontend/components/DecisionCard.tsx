import { useState } from 'react';
import ProductImage from './ProductImage';

interface Decision {
  id: string;
  type: 'BUY' | 'DO_NOT_BUY' | 'ASK_USER';
  category: string;
  confidence: number;
  reasoning: string[];
  product?: any;
  inventoryState: string;
  depletionEstimate: string;
}

export default function DecisionCard({ decision }: { decision: Decision }) {
  const [expanded, setExpanded] = useState(false);

  const getTheme = () => {
    switch(decision.type) {
      case 'BUY': return { border: 'border-green-200', bg: 'bg-green-50', text: 'text-green-800', badge: 'bg-green-100', icon: '✓ AUTOPURCHASE RECOMMENDED' };
      case 'DO_NOT_BUY': return { border: 'border-neutral-200', bg: 'bg-white', text: 'text-neutral-700', badge: 'bg-neutral-100', icon: '✓ NO PURCHASE REQUIRED' };
      case 'ASK_USER': return { border: 'border-orange-200', bg: 'bg-orange-50', text: 'text-orange-800', badge: 'bg-orange-100', icon: '! NEEDS YOUR DECISION' };
      default: return { border: 'border-neutral-200', bg: 'bg-white', text: 'text-neutral-800', badge: 'bg-neutral-100', icon: '' };
    }
  };

  const theme = getTheme();

  return (
    <div className={`border ${theme.border} ${theme.bg} rounded-2xl overflow-hidden shadow-sm transition-all mb-4`}>
      <div className="p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h3 className="text-xl font-bold text-neutral-900 tracking-tight mb-2 uppercase">{decision.category}</h3>
            <div className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${theme.badge} ${theme.text}`}>
              {theme.icon}
            </div>
          </div>
          
          <div className="text-right flex flex-col items-end">
            <div className="text-sm text-neutral-500 font-medium mb-1">Confidence</div>
            <div className={`text-xl font-bold ${decision.confidence > 80 ? 'text-green-600' : 'text-orange-500'}`}>
              {decision.confidence}%
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
          <div>
            <div className="text-xs text-neutral-500 mb-1 font-medium">Estimated inventory</div>
            <div className="text-sm font-semibold text-neutral-900">{decision.inventoryState}</div>
          </div>
          <div>
            <div className="text-xs text-neutral-500 mb-1 font-medium">Expected depletion</div>
            <div className="text-sm font-semibold text-neutral-900">{decision.depletionEstimate}</div>
          </div>
          
          {decision.product && (
            <>
              <div>
                <div className="text-xs text-neutral-500 mb-1 font-medium">Selected product</div>
                <div className="text-sm font-semibold text-neutral-900 line-clamp-1">{decision.product.name}</div>
              </div>
              <div>
                <div className="text-xs text-neutral-500 mb-1 font-medium">Cost</div>
                <div className="text-sm font-semibold text-neutral-900">₹{decision.product.price}</div>
              </div>
            </>
          )}
        </div>

        <div className="flex flex-wrap gap-3">
          {decision.type === 'BUY' && (
            <>
              <button className="px-5 py-2.5 bg-neutral-900 text-white rounded-xl text-sm font-semibold hover:bg-neutral-800 transition-colors">
                Let Autopilot Handle It
              </button>
              <button onClick={() => setExpanded(!expanded)} className="px-5 py-2.5 bg-white border border-neutral-300 text-neutral-700 rounded-xl text-sm font-semibold hover:bg-neutral-50 transition-colors">
                {expanded ? 'Hide Reasoning' : 'Review'}
              </button>
            </>
          )}
          
          {decision.type === 'ASK_USER' && (
            <>
              <button className="px-5 py-2.5 bg-orange-600 text-white rounded-xl text-sm font-semibold hover:bg-orange-700 transition-colors">
                Review & Approve
              </button>
              <button onClick={() => setExpanded(!expanded)} className="px-5 py-2.5 bg-white border border-neutral-300 text-neutral-700 rounded-xl text-sm font-semibold hover:bg-neutral-50 transition-colors">
                {expanded ? 'Hide Reasoning' : 'Why ask me?'}
              </button>
            </>
          )}

          {decision.type === 'DO_NOT_BUY' && (
            <button onClick={() => setExpanded(!expanded)} className="px-5 py-2.5 bg-white border border-neutral-300 text-neutral-700 rounded-xl text-sm font-semibold hover:bg-neutral-50 transition-colors">
              {expanded ? 'Hide Reasoning' : 'Why did you ignore this?'}
            </button>
          )}
        </div>
      </div>
      
      {expanded && (
        <div className="border-t border-neutral-200/50 bg-white/50 p-6">
          <h4 className="text-sm font-bold text-neutral-900 mb-4 uppercase tracking-wider">Decision Reasoning</h4>
          <ul className="space-y-3">
            {decision.reasoning.map((reason, idx) => (
              <li key={idx} className="flex items-start gap-3 text-sm text-neutral-700">
                <span className="flex-shrink-0 w-5 h-5 rounded-full bg-neutral-200 flex items-center justify-center text-xs font-bold text-neutral-600 mt-0.5">{idx + 1}</span>
                <span className="pt-0.5">{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
