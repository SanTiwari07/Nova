"use client";

import { useState } from "react";
import { Check } from "lucide-react";

type AutoLevel = 0 | 1 | 2 | 3;

const LEVEL_CONFIG: Record<AutoLevel, { label: string; description: string; color: string }> = {
  0: { label: "Suggest only", description: "NOVA can recommend. You do everything.", color: "bg-neutral-100 text-neutral-700" },
  1: { label: "Prepare cart", description: "NOVA prepares the shopping plan. You approve and checkout.", color: "bg-blue-100 text-blue-700" },
  2: { label: "Handle routine items", description: "NOVA automatically handles routine purchases within your limits.", color: "bg-orange-100 text-orange-700" },
  3: { label: "Full autopilot", description: "NOVA handles all qualifying purchases. You are notified afterwards.", color: "bg-green-100 text-green-700" },
};

export default function RulesPage() {
  const [autoLevel, setAutoLevel] = useState<AutoLevel>(2);
  const [autoLimit, setAutoLimit] = useState(500);
  const [monthlyLimit, setMonthlyLimit] = useState(5500);
  const [primeOnly, setPrimeOnly] = useState(true);
  const [allowSubs, setAllowSubs] = useState(true);
  const [allowedCats, setAllowedCats] = useState(["Grocery", "Household", "Personal Care"]);
  const [askAbove, setAskAbove] = useState(500);
  const [askNewBrands, setAskNewBrands] = useState(true);
  const [askPriceIncrease, setAskPriceIncrease] = useState(15);
  const [saved, setSaved] = useState(false);

  const allCats = ["Grocery", "Household", "Personal Care", "Electronics", "Clothing", "Furniture"];

  const toggleCat = (cat: string) => {
    setAllowedCats(prev => prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#FCFBF9]">
      <div className="max-w-3xl mx-auto px-4 md:px-8 py-8">

        {/* Header */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-2">NOVA · User Control</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Autopilot Control</h1>
          <p className="text-neutral-500">You control exactly what NOVA is allowed to do. Always.</p>
        </div>

        {/* Key message */}
        <div className="bg-neutral-900 text-white rounded-2xl p-5 mb-8">
          <p className="text-sm font-semibold leading-relaxed">
            NOVA can prepare the order. <span className="text-[#FF9900]">You control the money.</span>
            <br />
            Nothing outside your rules can be purchased automatically.
          </p>
        </div>

        {/* Autonomy level */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-6">
          <h2 className="text-lg font-black text-neutral-900 mb-4">Autonomy level</h2>
          <div className="grid grid-cols-2 gap-3">
            {([0, 1, 2, 3] as AutoLevel[]).map(level => {
              const cfg = LEVEL_CONFIG[level];
              return (
                <button
                  key={level}
                  onClick={() => setAutoLevel(level)}
                  className={`p-4 rounded-2xl border-2 text-left transition-all ${autoLevel === level ? "border-neutral-900 shadow-sm" : "border-neutral-200 hover:border-neutral-400"}`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${cfg.color}`}>Level {level}</span>
                  </div>
                  <p className="text-sm font-bold text-neutral-900">{cfg.label}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">{cfg.description}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Money limits */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-6">
          <h2 className="text-lg font-black text-neutral-900 mb-4">Money limits</h2>
          <div className="space-y-5">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-neutral-700">Maximum per item (auto)</label>
                <span className="text-sm font-black text-neutral-900">₹{autoLimit}</span>
              </div>
              <input
                type="range" min={100} max={2000} step={100} value={autoLimit}
                onChange={e => setAutoLimit(Number(e.target.value))}
                className="w-full accent-[#FF9900]"
              />
              <div className="flex justify-between mt-0.5">
                <span className="text-xs text-neutral-400">₹100</span>
                <span className="text-xs text-neutral-400">₹2,000</span>
              </div>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-neutral-700">Monthly auto-purchase limit</label>
                <span className="text-sm font-black text-neutral-900">₹{monthlyLimit.toLocaleString("en-IN")}</span>
              </div>
              <input
                type="range" min={1000} max={15000} step={500} value={monthlyLimit}
                onChange={e => setMonthlyLimit(Number(e.target.value))}
                className="w-full accent-[#FF9900]"
              />
            </div>
          </div>
        </div>

        {/* Allowed categories */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-6">
          <h2 className="text-lg font-black text-neutral-900 mb-4">Purchasing categories</h2>
          <p className="text-sm text-neutral-500 mb-4">NOVA can automatically purchase from these categories.</p>
          <div className="flex flex-wrap gap-2">
            {allCats.map(cat => (
              <button
                key={cat}
                onClick={() => toggleCat(cat)}
                className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all flex items-center gap-1.5 ${allowedCats.includes(cat) ? "bg-neutral-900 text-white" : "bg-neutral-100 text-neutral-600 hover:bg-neutral-200"}`}
              >
                {allowedCats.includes(cat) && <Check className="w-3.5 h-3.5" />}
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Product rules */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-6">
          <h2 className="text-lg font-black text-neutral-900 mb-4">Product rules</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-2xl">
              <div>
                <p className="text-sm font-semibold text-neutral-900">Prime eligible only</p>
                <p className="text-xs text-neutral-500">Only purchase items with Amazon Prime delivery</p>
              </div>
              <button
                onClick={() => setPrimeOnly(!primeOnly)}
                className={`w-12 h-6 rounded-full transition-all relative ${primeOnly ? "bg-[#FF9900]" : "bg-neutral-200"}`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow absolute top-0.5 transition-all ${primeOnly ? "right-0.5" : "left-0.5"}`}></div>
              </button>
            </div>
            <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-2xl">
              <div>
                <p className="text-sm font-semibold text-neutral-900">Allow substitutions</p>
                <p className="text-xs text-neutral-500">If usual brand is unavailable, NOVA can use similar products</p>
              </div>
              <button
                onClick={() => setAllowSubs(!allowSubs)}
                className={`w-12 h-6 rounded-full transition-all relative ${allowSubs ? "bg-[#FF9900]" : "bg-neutral-200"}`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow absolute top-0.5 transition-all ${allowSubs ? "right-0.5" : "left-0.5"}`}></div>
              </button>
            </div>
          </div>
        </div>

        {/* Human approval triggers */}
        <div className="bg-white rounded-3xl border border-neutral-200 p-6 mb-6">
          <h2 className="text-lg font-black text-neutral-900 mb-4">Always ask me when</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-neutral-700">Purchase above</label>
                <span className="text-sm font-black text-neutral-900">₹{askAbove}</span>
              </div>
              <input
                type="range" min={100} max={2000} step={100} value={askAbove}
                onChange={e => setAskAbove(Number(e.target.value))}
                className="w-full accent-[#FF9900]"
              />
            </div>
            <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-2xl">
              <div>
                <p className="text-sm font-semibold text-neutral-900">New brands</p>
                <p className="text-xs text-neutral-500">Ask before purchasing a brand not in household memory</p>
              </div>
              <button
                onClick={() => setAskNewBrands(!askNewBrands)}
                className={`w-12 h-6 rounded-full transition-all relative ${askNewBrands ? "bg-[#FF9900]" : "bg-neutral-200"}`}
              >
                <div className={`w-5 h-5 rounded-full bg-white shadow absolute top-0.5 transition-all ${askNewBrands ? "right-0.5" : "left-0.5"}`}></div>
              </button>
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-neutral-700">Price increase above</label>
                <span className="text-sm font-black text-neutral-900">{askPriceIncrease}% vs average</span>
              </div>
              <input
                type="range" min={5} max={50} step={5} value={askPriceIncrease}
                onChange={e => setAskPriceIncrease(Number(e.target.value))}
                className="w-full accent-[#FF9900]"
              />
            </div>
          </div>
        </div>

        {/* Save */}
        <button
          onClick={handleSave}
          className={`w-full py-4 rounded-2xl font-bold text-base transition-all flex items-center justify-center gap-2 ${saved ? "bg-green-500 text-white" : "bg-neutral-900 text-white hover:bg-neutral-800"}`}
        >
          {saved ? (
            <>
              <Check className="w-5 h-5" /> Rules saved
            </>
          ) : (
            "Save Autopilot Rules"
          )}
        </button>
        <p className="text-xs text-center text-neutral-400 mt-2">
          Changes take effect immediately. NOVA will re-evaluate pending items.
        </p>
      </div>
    </div>
  );
}
