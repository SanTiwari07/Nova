export default function AmazonConnectionBadge({ size = "sm" }: { size?: "sm" | "lg" }) {
  return (
    <div className={`inline-flex items-center gap-1.5 px-3 ${size === "lg" ? "py-2" : "py-1.5"} bg-orange-50 border border-orange-200 rounded-full`}>
      <div className="w-1.5 h-1.5 rounded-full bg-orange-400"></div>
      <span className={`font-semibold text-orange-700 ${size === "lg" ? "text-sm" : "text-xs"}`}>Amazon · Demo Mode</span>
    </div>
  );
}
