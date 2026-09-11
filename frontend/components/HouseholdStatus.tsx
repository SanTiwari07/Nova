interface HouseholdStatusProps {
  trackedItems: number;
  healthPercent: number;
  budgetRemaining: number;
  autonomyOn: boolean;
  decisionsCount: number;
}

export default function HouseholdStatus({
  trackedItems,
  healthPercent,
  budgetRemaining,
  autonomyOn,
  decisionsCount
}: HouseholdStatusProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
      <div className="bg-white border border-neutral-200 rounded-2xl p-5 shadow-sm">
        <span className="text-xs font-bold tracking-wider text-neutral-500 block mb-2 uppercase">Inventory</span>
        <div className="text-3xl font-extrabold text-neutral-900 mb-1">{healthPercent}%</div>
        <p className="text-xs text-neutral-500">{trackedItems} tracked items</p>
      </div>
      
      <div className="bg-white border border-neutral-200 rounded-2xl p-5 shadow-sm">
        <span className="text-xs font-bold tracking-wider text-neutral-500 block mb-2 uppercase">Budget</span>
        <div className="text-3xl font-extrabold text-neutral-900 mb-1">₹{budgetRemaining}</div>
        <p className="text-xs text-neutral-500">remaining</p>
      </div>

      <div className="bg-white border border-neutral-200 rounded-2xl p-5 shadow-sm">
        <span className="text-xs font-bold tracking-wider text-neutral-500 block mb-2 uppercase">Autopilot</span>
        <div className="flex items-center gap-2 mb-1">
          <div className={`w-3 h-3 rounded-full ${autonomyOn ? 'bg-green-500' : 'bg-neutral-300'}`}></div>
          <div className="text-3xl font-extrabold text-neutral-900">{autonomyOn ? 'ON' : 'OFF'}</div>
        </div>
        <p className="text-xs text-neutral-500">autonomous actions</p>
      </div>

      <div className={`border rounded-2xl p-5 shadow-sm ${decisionsCount > 0 ? 'bg-orange-50 border-orange-200' : 'bg-white border-neutral-200'}`}>
        <span className={`text-xs font-bold tracking-wider uppercase block mb-2 ${decisionsCount > 0 ? 'text-orange-700' : 'text-neutral-500'}`}>Decisions</span>
        <div className={`text-3xl font-extrabold mb-1 ${decisionsCount > 0 ? 'text-orange-600' : 'text-neutral-900'}`}>{decisionsCount}</div>
        <p className={`text-xs ${decisionsCount > 0 ? 'text-orange-700' : 'text-neutral-500'}`}>
          {decisionsCount > 0 ? 'needs your attention' : 'all caught up'}
        </p>
      </div>
    </div>
  );
}
