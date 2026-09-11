"use client";

import { useState, useEffect } from "react";

export default function MemoryPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetch("/api/purchase-history")
      .then(r => r.json())
      .then(data => setProducts(data?.products || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const filtered = products.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.brand.toLowerCase().includes(search.toLowerCase()) ||
    p.category.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-[#FCFBF9]">
      <div className="max-w-4xl mx-auto px-4 md:px-8 py-8">

        {/* Header */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-2">Amazon · Demo data</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Household Memory</h1>
          <p className="text-neutral-500">NOVA knows your household. Here is everything it has learned from your Amazon orders.</p>
        </div>

        {/* Search */}
        <div className="relative mb-6">
          <svg className="absolute left-4 top-1/2 -translate-y-1/2 text-neutral-400" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search products..."
            className="w-full pl-11 pr-4 py-3 bg-white border border-neutral-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent"
          />
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {filtered.map(product => (
              <MemoryCard key={product.product_id} product={product} />
            ))}
            {filtered.length === 0 && (
              <div className="text-center py-12 bg-white rounded-2xl border border-neutral-200">
                <p className="text-neutral-500">No products match your search.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function MemoryCard({ product }: { product: any }) {
  const [expanded, setExpanded] = useState(false);
  const priceDiff = product.current_price - product.avg_price;
  const belowAvg = priceDiff < 0;
  const needsSoon = product.days_until_needed <= 7;

  return (
    <div className="bg-white rounded-2xl border border-neutral-200 hover:shadow-sm transition-all overflow-hidden">
      <button className="w-full p-5 text-left" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start gap-4">
          {/* Brand + Name */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap mb-1">
              <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider">{product.brand}</p>
              <span className="text-[9px] font-bold px-2 py-0.5 bg-neutral-100 text-neutral-500 rounded-full">{product.category}</span>
              {needsSoon && (
                <span className="text-[9px] font-bold px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full">Due in {product.days_until_needed}d</span>
              )}
            </div>
            <p className="text-sm font-semibold text-neutral-900">{product.name}</p>
            <p className="text-xs text-neutral-400">{product.pack_size}</p>
          </div>

          {/* Key stats */}
          <div className="flex items-center gap-4 shrink-0">
            <div className="text-right">
              <p className="text-lg font-black text-neutral-900">₹{product.current_price}</p>
              <p className={`text-xs font-semibold ${belowAvg ? "text-green-600" : "text-red-500"}`}>
                {belowAvg ? `₹${Math.abs(priceDiff)} below avg` : `₹${priceDiff} above avg`}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm font-bold text-neutral-900">{Math.round(product.confidence * 100)}%</p>
              <p className="text-xs text-neutral-400">confidence</p>
            </div>
            <svg className={`text-neutral-300 transition-transform ${expanded ? "rotate-180" : ""}`} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
          </div>
        </div>
      </button>

      {expanded && (
        <div className="border-t border-neutral-100 bg-neutral-50 p-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            {[
              { label: "Purchased", value: `${product.purchase_count} times` },
              { label: "Typical interval", value: `${product.typical_interval_days} days` },
              { label: "Typical quantity", value: String(product.typical_quantity) },
              { label: "Average price", value: `₹${product.avg_price}` },
              { label: "Lowest seen", value: `₹${product.lowest_price}` },
              { label: "Last price", value: `₹${product.last_price}` },
              { label: "Next expected", value: `In ${product.days_until_needed} days` },
              { label: "Preferred brand", value: product.preferred_brand },
            ].map(stat => (
              <div key={stat.label}>
                <p className="text-xs text-neutral-400 mb-0.5">{stat.label}</p>
                <p className="text-sm font-semibold text-neutral-900">{stat.value}</p>
              </div>
            ))}
          </div>

          {/* NOVA insight */}
          <div className="p-3 bg-orange-50 rounded-xl border border-orange-100">
            <p className="text-xs text-orange-800 leading-relaxed">
              <strong>NOVA knows:</strong> You usually buy {product.name} every {product.typical_interval_days} days. Your last purchase was {Math.floor((Date.now() - new Date(product.last_purchase_date).getTime()) / 86400000)} days ago. Next expected in {product.days_until_needed} days.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-2 mt-3">
            <button className="px-3 py-1.5 text-xs font-semibold text-neutral-600 bg-white border border-neutral-200 rounded-lg hover:border-neutral-400 transition-colors">
              Mark one-time
            </button>
            <button className="px-3 py-1.5 text-xs font-semibold text-neutral-600 bg-white border border-neutral-200 rounded-lg hover:border-neutral-400 transition-colors">
              Change interval
            </button>
            <button className="px-3 py-1.5 text-xs font-semibold text-neutral-600 bg-white border border-neutral-200 rounded-lg hover:border-neutral-400 transition-colors">
              Change brand
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
