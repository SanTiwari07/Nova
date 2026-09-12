"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import ProductImage from "@/components/ProductImage";
import { ShoppingBag, TrendingDown, RefreshCw, CheckCircle2, ArrowRight } from "lucide-react";

export default function NovaCartPage() {
  const [cart, setCart] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [removed, setRemoved] = useState<Set<string>>(new Set());
  const [approving, setApproving] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/nova-cart")
      .then(r => r.json())
      .then(data => {
        setCart(data);
        const initQty: Record<string, number> = {};
        (data?.items || []).forEach((i: any) => { initQty[i.product_id] = i.quantity || 1; });
        setQuantities(initQty);
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleApprove = async (productId: string) => {
    setApproving(productId);
    await fetch("/api/autopilot/approve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId, approved: true, quantity: quantities[productId] }),
    });
    setApproving(null);
  };

  const handleRemove = (productId: string) => {
    setRemoved(prev => {
      const next = new Set(prev);
      next.add(productId);
      return next;
    });
  };

  const router = useRouter();
  const [syncing, setSyncing] = useState(false);
  const [syncSuccess, setSyncSuccess] = useState(false);

  const handleSendToCart = async () => {
    setSyncing(true);
    try {
      const activeItems = (cart?.items || []).filter((i: any) => !removed.has(i.product_id));
      for (const item of activeItems) {
        await fetch("/api/cart/add", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ product_id: item.product_id, quantity: quantities[item.product_id] || 1 }),
        }).catch(() => {});
      }
      setSyncSuccess(true);
      window.dispatchEvent(new Event("cart-updated"));
      setTimeout(() => {
        router.push("/cart");
      }, 1200);
    } catch (err) {
      console.error(err);
    } finally {
      setSyncing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FCFBF9] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin"></div>
          <p className="text-neutral-500 text-sm font-medium">NOVA is preparing your household cart...</p>
        </div>
      </div>
    );
  }

  const items = (cart?.items || []).filter((i: any) => !removed.has(i.product_id));
  const autoItems = items.filter((i: any) => !i.requires_approval);
  const approvalItems = items.filter((i: any) => i.requires_approval);
  const total = items.reduce((s: number, i: any) => s + (i.current_price * (quantities[i.product_id] || 1)), 0);
  const budgetRemaining = cart?.budget_remaining || 0;

  return (
    <div className="min-h-screen bg-[#FCFBF9]">
      <div className="max-w-5xl mx-auto px-4 md:px-8 py-8">

        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-bold tracking-widest text-neutral-400 uppercase">Amazon · Demo data</span>
          </div>
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-black text-neutral-900 tracking-tight">Your household cart</h1>
              <p className="text-neutral-500 mt-1">NOVA prepared {items.length} items for your Amazon order</p>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-sm text-neutral-500">Estimated total</p>
                <p className="text-2xl font-black text-neutral-900">₹{total.toLocaleString("en-IN")}</p>
              </div>
              <div className={`text-right px-4 py-2 rounded-xl border ${total <= budgetRemaining ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}>
                <p className="text-xs text-neutral-500">Budget left</p>
                <p className={`text-sm font-bold ${total <= budgetRemaining ? "text-green-700" : "text-red-700"}`}>
                  ₹{budgetRemaining.toLocaleString("en-IN")}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Auto items */}
        {autoItems.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-green-100 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs font-bold text-green-700">NOVA recommends</span>
              </div>
              <p className="text-sm text-neutral-500">{autoItems.length} items ready</p>
            </div>
            <div className="space-y-3">
              {autoItems.map((item: any) => (
                <CartItemRow
                  key={item.product_id}
                  item={item}
                  quantity={quantities[item.product_id] || 1}
                  onQtyChange={(q: number) => setQuantities(prev => ({ ...prev, [item.product_id]: q }))}
                  onRemove={() => handleRemove(item.product_id)}
                />
              ))}
            </div>
          </div>
        )}

        {/* Approval items */}
        {approvalItems.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex items-center gap-2 px-3 py-1.5 bg-orange-100 rounded-full">
                <span className="text-xs font-bold text-orange-700">Needs your okay</span>
              </div>
              <p className="text-sm text-neutral-500">{approvalItems.length} item{approvalItems.length > 1 ? "s" : ""} to review</p>
            </div>
            <div className="space-y-3">
              {approvalItems.map((item: any) => (
                <CartItemRow
                  key={item.product_id}
                  item={item}
                  quantity={quantities[item.product_id] || 1}
                  onQtyChange={(q: number) => setQuantities(prev => ({ ...prev, [item.product_id]: q }))}
                  onRemove={() => handleRemove(item.product_id)}
                  requiresApproval
                  approving={approving === item.product_id}
                  onApprove={() => handleApprove(item.product_id)}
                />
              ))}
            </div>
          </div>
        )}

        {items.length === 0 && (
          <div className="text-center py-16 bg-white rounded-2xl border border-neutral-200">
            <ShoppingBag className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
            <p className="text-neutral-500 font-medium">Your NOVA Cart is empty.</p>
            <Link href="/store" className="mt-4 inline-flex items-center gap-1 text-[#FF9900] font-semibold hover:underline">
              Browse household items &rarr;
            </Link>
          </div>
        )}

        {/* Checkout area */}
        {items.length > 0 && (
          <div className="bg-white rounded-3xl border border-neutral-200 p-6 sticky bottom-4">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <p className="text-neutral-500 text-sm mb-1">{autoItems.length} automatic + {approvalItems.length} pending approval</p>
                <p className="text-2xl font-black text-neutral-900">₹{total.toLocaleString("en-IN")} total</p>
              </div>
              <div className="flex flex-col gap-2">
                <button
                  disabled={syncing}
                  className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-[#FF9900] text-white font-bold rounded-xl hover:bg-[#e68900] transition-colors text-sm disabled:opacity-50"
                  onClick={handleSendToCart}
                >
                  {syncing ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" /> Synchronizing Cart...
                    </>
                  ) : syncSuccess ? (
                    <>
                      <CheckCircle2 className="w-4 h-4" /> Synchronized! Redirecting...
                    </>
                  ) : (
                    <>
                      <ShoppingBag className="w-4 h-4" /> Send to Commerce Cart &rarr;
                    </>
                  )}
                </button>
                <p className="text-xs text-center text-neutral-400">Deterministic validation &middot; Budget protected</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function CartItemRow({ item, quantity, onQtyChange, onRemove, requiresApproval = false, approving = false, onApprove }: any) {
  const [showWhy, setShowWhy] = useState(false);
  const total = item.current_price * quantity;
  const priceDiff = item.current_price - item.avg_price;
  const belowAvg = priceDiff < 0;

  return (
    <div className={`bg-white rounded-2xl border ${requiresApproval ? "border-orange-200" : "border-neutral-200"} p-4 md:p-5 hover:shadow-sm transition-all`}>
      <div className="flex gap-4">
        {/* Image */}
        <div className="w-16 h-16 md:w-20 md:h-20 rounded-xl overflow-hidden bg-neutral-100 shrink-0">
          <ProductImage src={item.imageUrl || item.image} alt={item.name} category={item.category} product={item} fill={false} />
        </div>

        {/* Details */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider">{item.brand}</p>
              <p className="text-sm font-semibold text-neutral-900 leading-snug">{item.name}</p>
              <p className="text-xs text-neutral-400">{item.pack_size}</p>
            </div>
            <button onClick={onRemove} className="text-neutral-300 hover:text-red-500 transition-colors shrink-0 mt-0.5">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          {/* Price + NOVA intelligence */}
          <div className="flex flex-wrap items-center gap-3 mt-2">
            <div>
              <span className="text-lg font-black text-neutral-900">₹{item.current_price}</span>
              {item.avg_price && (
                <span className={`ml-2 text-xs flex items-center gap-1 ${belowAvg ? "text-green-600" : "text-neutral-400"}`}>
                  {belowAvg && <TrendingDown className="w-3.5 h-3.5 text-green-600 inline" />}
                  {belowAvg ? `₹${Math.abs(priceDiff)} below avg` : `₹${priceDiff} above avg`}
                </span>
              )}
            </div>
            <div className="flex items-center gap-1 text-xs text-neutral-500">
              <span>Every {item.typical_interval_days}d</span>
              <span className="text-neutral-300">·</span>
              <span>In {item.days_until_needed}d</span>
              <span className="text-neutral-300">·</span>
              <span className={item.confidence >= 0.9 ? "text-green-600 font-semibold" : "text-neutral-500"}>{Math.round((item.confidence || 0.85) * 100)}% conf</span>
            </div>
          </div>

          {/* Reason + Why button */}
          <div className="mt-2 flex items-center gap-2">
            <p className="text-xs text-neutral-500 flex-1 line-clamp-1">{item.reason}</p>
            <button onClick={() => setShowWhy(!showWhy)} className="text-xs text-[#FF9900] font-semibold hover:underline shrink-0">
              {showWhy ? "Close" : "Why?"}
            </button>
          </div>

          {showWhy && (
            <div className="mt-2 p-3 bg-orange-50 rounded-xl border border-orange-100">
              <p className="text-xs text-neutral-700 leading-relaxed">{item.reason}</p>
              <p className="text-xs text-neutral-500 mt-1">Confidence: {Math.round((item.confidence || 0.85) * 100)}% · Amazon price: ₹{item.current_price}</p>
            </div>
          )}

          {/* Qty + Actions */}
          <div className="flex items-center gap-3 mt-3">
            <div className="flex items-center gap-1 border border-neutral-200 rounded-lg overflow-hidden">
              <button onClick={() => onQtyChange(Math.max(1, quantity - 1))} className="px-2.5 py-1 text-neutral-600 hover:bg-neutral-100 transition-colors text-sm">-</button>
              <span className="px-3 py-1 text-sm font-semibold text-neutral-900 bg-neutral-50">{quantity}</span>
              <button onClick={() => onQtyChange(quantity + 1)} className="px-2.5 py-1 text-neutral-600 hover:bg-neutral-100 transition-colors text-sm">+</button>
            </div>
            <span className="text-sm font-bold text-neutral-900">= ₹{total.toLocaleString("en-IN")}</span>
            {requiresApproval && (
              <button
                onClick={onApprove}
                disabled={approving}
                className="ml-auto px-4 py-1.5 bg-[#FF9900] text-white text-xs font-bold rounded-lg hover:bg-[#e68900] disabled:opacity-50 transition-colors"
              >
                {approving ? "Approving..." : "Approve"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
