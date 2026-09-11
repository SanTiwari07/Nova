interface SavingsCardProps {
  opportunity: {
    type: string;
    product_name: string;
    current_price: number;
    target_price: number;
    potential_saving: number;
    reason: string;
    action: string;
  };
}

export default function SavingsCard({ opportunity }: SavingsCardProps) {
  return (
    <div className="p-4 bg-green-50 rounded-2xl border border-green-100 hover:shadow-sm transition-all">
      <div className="flex items-start justify-between gap-3 mb-2">
        <p className="text-sm font-semibold text-neutral-900">{opportunity.product_name}</p>
        <span className="text-base font-black text-green-700 shrink-0">₹{opportunity.potential_saving}</span>
      </div>
      <p className="text-xs text-neutral-600 mb-3">{opportunity.reason}</p>
      <div className="flex items-center gap-2">
        <span className="text-xs text-neutral-400">₹{opportunity.current_price} → ₹{opportunity.target_price}</span>
        <span className="text-xs font-semibold text-green-700 ml-auto">{opportunity.action}</span>
      </div>
    </div>
  );
}
