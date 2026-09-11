interface PriceSignalCardProps {
  current: number;
  typical: number;
  lowest: number;
  recommendation: "BUY" | "WAIT";
  reason: string;
}

export default function PriceSignalCard({ current, typical, lowest, recommendation, reason }: PriceSignalCardProps) {
  const pct = ((current - typical) / typical * 100).toFixed(1);
  const isBuy = recommendation === "BUY";

  return (
    <div className={`p-4 rounded-2xl border ${isBuy ? "bg-green-50 border-green-100" : "bg-blue-50 border-blue-100"}`}>
      <div className="flex items-center gap-2 mb-3">
        <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${isBuy ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}`}>{recommendation}</span>
        <span className={`text-xs font-semibold ${Number(pct) > 0 ? "text-red-500" : "text-green-600"}`}>
          {Number(pct) > 0 ? "+" : ""}{pct}% vs avg
        </span>
      </div>
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="text-center">
          <p className="text-xs text-neutral-400">Now</p>
          <p className="text-sm font-black text-neutral-900">₹{current}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-neutral-400">Typical</p>
          <p className="text-sm font-black text-neutral-500">₹{typical}</p>
        </div>
        <div className="text-center">
          <p className="text-xs text-neutral-400">Lowest</p>
          <p className="text-sm font-black text-green-700">₹{lowest}</p>
        </div>
      </div>
      <p className="text-xs text-neutral-600">{reason}</p>
    </div>
  );
}
