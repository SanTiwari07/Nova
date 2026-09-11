"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function PriceWatchPage() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [watchingIds, setWatchingIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetch("/api/price-watch")
      .then(r => r.json())
      .then(data => {
        setItems(data?.items || []);
        const watching = new Set<string>((data?.items || []).filter((i: any) => i.watching).map((i: any) => i.product_id));
        setWatchingIds(watching);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const toggleWatch = (productId: string) => {
    setWatchingIds(prev => {
      const next = new Set(prev);
      if (next.has(productId)) next.delete(productId);
      else next.add(productId);
      return next;
    });
  };

  const buyItems = items.filter(i => i.recommendation === "BUY");
  const waitItems = items.filter(i => i.recommendation === "WAIT");

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FCFBF9] flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FCFBF9]">
      <div className="max-w-4xl mx-auto px-4 md:px-8 py-8">

        {/* Header */}
        <div className="mb-8">
          <p className="text-xs font-bold tracking-widest text-neutral-400 uppercase mb-2">Amazon · Demo data</p>
          <h1 className="text-3xl font-black text-neutral-900 tracking-tight mb-2">Price Watch</h1>
          <p className="text-neutral-500">Buy now or wait? NOVA connects Amazon prices to your household needs.</p>
        </div>

        {/* BUY section */}
        {buyItems.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <span className="px-3 py-1 bg-green-100 text-green-700 text-xs font-bold rounded-full">BUY NOW</span>
              <p className="text-sm text-neutral-500">Good time to purchase</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {buyItems.map(item => (
                <PriceCard key={item.product_id} item={item} watching={watchingIds.has(item.product_id)} onToggleWatch={() => toggleWatch(item.product_id)} />
              ))}
            </div>
          </div>
        )}

        {/* WAIT section */}
        {waitItems.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-4">
              <span className="px-3 py-1 bg-blue-100 text-blue-700 text-xs font-bold rounded-full">WAIT</span>
              <p className="text-sm text-neutral-500">Price is above your usual — no rush to buy</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {waitItems.map(item => (
                <PriceCard key={item.product_id} item={item} watching={watchingIds.has(item.product_id)} onToggleWatch={() => toggleWatch(item.product_id)} />
              ))}
            </div>
          </div>
        )}

        {items.length === 0 && (
          <div className="text-center py-16 bg-white rounded-2xl border border-neutral-200">
            <p className="text-4xl mb-4">📊</p>
            <p className="text-neutral-500 font-medium">No items being tracked yet.</p>
            <Link href="/store" className="mt-3 inline-block text-[#FF9900] font-semibold hover:underline text-sm">Browse products →</Link>
          </div>
        )}
      </div>
    </div>
  );
}

function PriceCard({ item, watching, onToggleWatch }: { item: any; watching: boolean; onToggleWatch: () => void }) {
  const isBuy = item.recommendation === "BUY";
  const pricePct = item.price_vs_avg_pct;
  const trendIcon = item.price_trend === "FALLING" ? "↓" : item.price_trend === "RISING" ? "↑" : "→";
  const trendColor = item.price_trend === "FALLING" ? "text-green-600" : item.price_trend === "RISING" ? "text-red-500" : "text-neutral-500";

  return (
    <div className={`bg-white rounded-2xl border p-5 hover:shadow-md transition-all ${isBuy ? "border-green-200" : "border-blue-200"}`}>
      {/* Product header */}
      <div className="flex items-start justify-between gap-2 mb-4">
        <div>
          <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider">{item.brand}</p>
          <p className="text-sm font-semibold text-neutral-900 leading-snug mt-0.5">{item.name}</p>
          <p className="text-xs text-neutral-400">{item.pack_size}</p>
        </div>
        <span className={`shrink-0 px-2.5 py-1 rounded-full text-[10px] font-bold ${isBuy ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"}`}>
          {item.recommendation}
        </span>
      </div>

      {/* Price grid */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="text-center p-2 bg-neutral-50 rounded-xl">
          <p className="text-xs text-neutral-400 mb-1">Current</p>
          <p className="text-base font-black text-neutral-900">₹{item.current_price}</p>
          <p className={`text-xs font-bold ${trendColor}`}>{trendIcon}</p>
        </div>
        <div className="text-center p-2 bg-neutral-50 rounded-xl">
          <p className="text-xs text-neutral-400 mb-1">Typical</p>
          <p className="text-base font-black text-neutral-500">₹{item.typical_price}</p>
          <p className={`text-xs font-semibold ${pricePct > 0 ? "text-red-500" : "text-green-600"}`}>
            {pricePct > 0 ? `+${pricePct.toFixed(0)}%` : `${pricePct.toFixed(0)}%`}
          </p>
        </div>
        <div className="text-center p-2 bg-neutral-50 rounded-xl">
          <p className="text-xs text-neutral-400 mb-1">Lowest</p>
          <p className="text-base font-black text-green-700">₹{item.lowest_observed}</p>
        </div>
      </div>

      {/* Reason */}
      <p className="text-xs text-neutral-600 leading-relaxed mb-4">{item.recommendation_reason}</p>

      {/* Actions */}
      <div className="flex gap-2">
        {isBuy ? (
          <Link
            href="/nova-cart"
            className="flex-1 py-2 bg-[#FF9900] text-white text-xs font-bold rounded-xl text-center hover:bg-[#e68900] transition-colors"
          >
            Add to NOVA Cart
          </Link>
        ) : (
          <button
            onClick={onToggleWatch}
            className={`flex-1 py-2 text-xs font-bold rounded-xl transition-colors ${watching ? "bg-blue-100 text-blue-700" : "bg-neutral-100 text-neutral-700 hover:bg-blue-50 hover:text-blue-700"}`}
          >
            {watching ? "✓ Watching price" : "Watch price"}
          </button>
        )}
        <div className={`px-3 py-2 rounded-xl text-xs font-semibold ${item.days_remaining <= 7 ? "bg-red-50 text-red-600" : "bg-neutral-50 text-neutral-500"}`}>
          {item.days_remaining}d left
        </div>
      </div>
    </div>
  );
}
