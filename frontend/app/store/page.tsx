"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import ProductShelf from "@/components/ProductShelf";
import CommandBox from "@/components/CommandBox";
import CategoryCard from "@/components/CategoryCard";
import DecisionCard from "@/components/DecisionCard";

export default function StorePage() {
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<any>(null);
  const [products, setProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [novaCart, setNovaCart] = useState<any>(null);
  const [reminders, setReminders] = useState<any[]>([]);
  const [priceWatch, setPriceWatch] = useState<any[]>([]);
  const [decisions, setDecisions] = useState<any[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [statusRes, productsRes, catsRes, novaCartRes, remindersRes, priceWatchRes, pantryRes, budgetRes] =
          await Promise.all([
            fetch("/api/household-status").then(r => r.json()).catch(() => null),
            fetch("/api/products?limit=100").then(r => r.json()).catch(() => []),
            fetch("/api/products/categories").then(r => r.json()).catch(() => []),
            fetch("/api/nova-cart").then(r => r.json()).catch(() => null),
            fetch("/api/reminders").then(r => r.json()).catch(() => { reminders: [] }),
            fetch("/api/price-watch").then(r => r.json()).catch(() => { items: [] }),
            fetch("/api/pantry").then(r => r.json()).catch(() => []),
            fetch("/api/budget").then(r => r.json()).catch(() => {}),
          ]);

        setStatus(statusRes);
        setProducts(productsRes || []);
        setCategories(catsRes || []);
        setNovaCart(novaCartRes);
        setReminders(remindersRes?.reminders || []);
        setPriceWatch(priceWatchRes?.items || []);

        // Build decisions from pantry
        const generatedDecisions: any[] = [];
        const milk = (pantryRes || []).find((i: any) => i.name.toLowerCase().includes("milk"));
        const oil = (pantryRes || []).find((i: any) => i.name.toLowerCase().includes("oil"));
        if (milk && milk.status === "LOW") {
          generatedDecisions.push({
            id: "d1", type: "BUY", category: "Milk", confidence: 92,
            inventoryState: `${milk.quantity}${milk.unit}`, depletionEstimate: "Tomorrow",
            product: { name: "Amul Taaza Milk 1L", price: 68 },
            reasoning: ["Inventory is low.", "Expected depletion: tomorrow.", "Amazon price ₹68 is within your ₹500 limit.", "Matches preferred brand (Amul)."],
          });
        }
        if (oil) {
          generatedDecisions.push({
            id: "d2", type: "DO_NOT_BUY", category: "Cooking Oil", confidence: 88,
            inventoryState: `${oil.quantity}${oil.unit}`, depletionEstimate: "~46 days",
            reasoning: ["Inventory is healthy.", "Current Amazon price ₹762 is 9% above average.", "No immediate purchase required."],
          });
        }
        setDecisions(generatedDecisions);
      } catch (err) {
        console.error("Failed to load store data", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FCFBF9] flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-10 h-10 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin"></div>
          <p className="text-neutral-500 font-medium text-sm">NOVA is checking your household...</p>
        </div>
      </div>
    );
  }

  // Product shelves
  const autopilotRecommends = (() => {
    const map = new Map();
    products.forEach(p => { if (!map.has(p.category)) map.set(p.category, { ...p, tags: ["recommended"] }); });
    return Array.from(map.values()).slice(0, 12);
  })();
  const usuals = products.filter(p => ["Tea","Coffee","Oil","Milk"].some(k => p.name.includes(k))).slice(0, 10).map(p => ({...p, tags: ["usual"]}));
  const groceries = products.filter(p => ["Rice","Atta","Dal","Oil","Salt","Sugar"].includes(p.category)).slice(0, 10);
  const household = products.filter(p => ["Detergent","Dishwash","Cleaning","Laundry","Soap"].includes(p.category)).slice(0, 10);
  const snacks = products.filter(p => ["Snacks","Beverages","Tea","Coffee"].includes(p.category)).slice(0, 10);

  const groceryCats = [
    { name: "Atta", key: "atta" }, { name: "Rice", key: "rice" }, { name: "Dal", key: "dal" },
    { name: "Oil", key: "oil" }, { name: "Tea", key: "tea" }, { name: "Coffee", key: "coffee" },
    { name: "Breakfast", key: "breakfast" }, { name: "Snacks", key: "snacks" },
    { name: "Noodles", key: "noodles" }, { name: "Biscuits", key: "biscuits" },
    { name: "Drinks", key: "drinks" }, { name: "Chocolates", key: "chocolates" },
  ];
  const householdCats = [
    { name: "Detergent", key: "detergent" }, { name: "Dishwash", key: "dishwash" },
    { name: "Bath & Body", key: "bath" }, { name: "Hair Care", key: "haircare" },
    { name: "Skin Care", key: "skincare" },
  ];

  const attentionReminders = reminders.filter(r => r.priority === "HIGH").slice(0, 3);
  const buyNowPrices = priceWatch.filter(p => p.recommendation === "BUY").slice(0, 4);

  return (
    <div className="min-h-screen bg-[#FCFBF9]">
      <div className="max-w-[1400px] mx-auto w-full">

        {/* ── SEARCH BAR ─────────────────────────────────────────────── */}
        <div className="px-4 md:px-8 pt-6 pb-4">
          <div className="relative max-w-3xl mx-auto">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              <svg className="text-neutral-400" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            </div>
            <Link href="/catalog">
              <div className="w-full pl-11 pr-6 py-4 rounded-2xl bg-white border border-neutral-200 shadow-sm text-neutral-400 font-medium text-base hover:border-neutral-400 hover:shadow-md transition-all cursor-text">
                What do you need today? &nbsp;<span className="text-neutral-300">— Try: "What should I reorder?" or "Check my Amazon orders"</span>
              </div>
            </Link>
          </div>
        </div>

        {/* ── HERO — HOUSEHOLD STATUS ─────────────────────────────────── */}
        <div className="px-4 md:px-8 pt-2 pb-6">
          <div className="bg-white rounded-3xl border border-neutral-200 shadow-sm p-6 md:p-8">
            {/* Header */}
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4 mb-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                  <span className="text-xs font-bold tracking-widest text-green-700 uppercase">Autopilot Active</span>
                </div>
                <h1 className="text-2xl md:text-3xl font-black text-neutral-900 tracking-tight leading-tight">
                  {status?.status_headline || "Your household is almost ready for September."}
                </h1>
                <p className="text-neutral-500 text-sm mt-1">NOVA analyzed your Amazon purchasing patterns.</p>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <Link
                  href="/autopilot"
                  className="px-5 py-2.5 bg-neutral-900 text-white rounded-xl text-sm font-semibold hover:bg-neutral-800 transition-colors"
                >
                  Review monthly cart
                </Link>
                <Link
                  href="/nova-cart"
                  className="px-5 py-2.5 bg-[#FF9900] text-white rounded-xl text-sm font-semibold hover:bg-[#e68900] transition-colors"
                >
                  NOVA Cart →
                </Link>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Tracked items", value: String(status?.tracked_items || 12), sub: "this month" },
                { label: "Due soon", value: String(status?.items_due_soon || 4), sub: "likely needed", highlight: "orange" },
                { label: "Est. monthly spend", value: `₹${(status?.estimated_monthly_spend || 2480).toLocaleString("en-IN")}`, sub: "projected" },
                { label: "Potential savings", value: `₹${(status?.potential_savings || 131).toLocaleString("en-IN")}`, sub: "identified", highlight: "green" },
              ].map((stat) => (
                <div key={stat.label} className={`p-4 rounded-2xl border ${stat.highlight === "green" ? "bg-green-50 border-green-100" : stat.highlight === "orange" ? "bg-orange-50 border-orange-100" : "bg-neutral-50 border-neutral-100"}`}>
                  <p className={`text-2xl md:text-3xl font-black ${stat.highlight === "green" ? "text-green-700" : stat.highlight === "orange" ? "text-orange-700" : "text-neutral-900"}`}>{stat.value}</p>
                  <p className={`text-xs font-semibold mt-0.5 ${stat.highlight === "green" ? "text-green-600" : stat.highlight === "orange" ? "text-orange-600" : "text-neutral-500"}`}>{stat.label}</p>
                  <p className="text-[11px] text-neutral-400 mt-0.5">{stat.sub}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── NOVA ATTENTION STRIP ────────────────────────────────────── */}
        {attentionReminders.length > 0 && (
          <div className="px-4 md:px-8 mb-6">
            <div className="flex items-center gap-2 mb-3">
              <span className="w-5 h-5 rounded-full bg-[#FF9900] flex items-center justify-center text-white text-[10px] font-bold">{attentionReminders.length}</span>
              <h2 className="text-sm font-bold text-neutral-900">Things that need attention</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {attentionReminders.map((rem) => (
                <Link key={rem.id} href={rem.action_url || "/reminders"}
                  className="flex items-start gap-3 p-4 bg-white rounded-2xl border border-neutral-200 hover:border-[#FF9900] hover:shadow-sm transition-all group">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${rem.type === "INVENTORY" ? "bg-red-100 text-red-600" : rem.type === "APPROVAL" ? "bg-orange-100 text-orange-600" : "bg-blue-100 text-blue-600"}`}>
                    {rem.type === "INVENTORY" ? "!" : rem.type === "APPROVAL" ? "?" : "i"}
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-neutral-900 group-hover:text-[#FF9900] transition-colors">{rem.title}</p>
                    <p className="text-xs text-neutral-500 mt-0.5 line-clamp-2">{rem.message}</p>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* ── NOVA CART PREVIEW ───────────────────────────────────────── */}
        {novaCart && novaCart.items && novaCart.items.length > 0 && (
          <div className="px-4 md:px-8 mb-8">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-xl font-black text-neutral-900 tracking-tight">Your household cart</h2>
                <p className="text-sm text-neutral-500">{novaCart.item_count} items NOVA prepared for Amazon</p>
              </div>
              <Link href="/nova-cart" className="text-sm font-semibold text-[#FF9900] hover:underline">Review all →</Link>
            </div>
            <div className="flex gap-4 overflow-x-auto pb-3 hide-scrollbar -mx-4 md:mx-0 px-4 md:px-0">
              {novaCart.items.slice(0, 6).map((item: any) => (
                <div key={item.product_id}
                  className="shrink-0 w-52 bg-white rounded-2xl border border-neutral-200 p-4 hover:shadow-md hover:border-neutral-300 transition-all">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider">{item.brand}</span>
                    {item.requires_approval
                      ? <span className="text-[9px] font-bold px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full">Needs ok</span>
                      : <span className="text-[9px] font-bold px-2 py-0.5 bg-green-100 text-green-700 rounded-full">Auto</span>
                    }
                  </div>
                  <p className="text-sm font-semibold text-neutral-900 line-clamp-2 mb-1">{item.name}</p>
                  <p className="text-xs text-neutral-400 mb-3">{item.pack_size}</p>
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-lg font-black text-neutral-900">₹{item.current_price}</p>
                      {item.avg_price && item.current_price < item.avg_price && (
                        <p className="text-[10px] text-green-600 font-semibold">Below avg ✓</p>
                      )}
                    </div>
                    <p className="text-[10px] text-neutral-400 text-right">{item.days_until_needed}d<br/>remaining</p>
                  </div>
                  <div className="mt-3 pt-3 border-t border-neutral-100">
                    <p className="text-[10px] text-neutral-400 leading-relaxed">{item.reason?.split(".")[0]}.</p>
                  </div>
                </div>
              ))}
            </div>
            {novaCart.approval_required_count > 0 && (
              <div className="mt-3 flex items-center gap-3 p-3 bg-orange-50 rounded-xl border border-orange-100">
                <span className="text-orange-600 text-sm">⚠</span>
                <p className="text-sm text-orange-800">
                  <span className="font-semibold">{novaCart.approval_required_count} item{novaCart.approval_required_count > 1 ? "s" : ""}</span> need{novaCart.approval_required_count === 1 ? "s" : ""} your approval.
                </p>
                <Link href="/nova-cart" className="ml-auto text-xs font-bold text-orange-700 hover:underline whitespace-nowrap">Review →</Link>
              </div>
            )}
          </div>
        )}

        {/* ── AUTOPILOT DECISIONS (MILK / OIL) ────────────────────────── */}
        {decisions.length > 0 && (
          <div id="decisions" className="px-4 md:px-8 mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-black text-neutral-900 tracking-tight">What NOVA decided</h2>
              <Link href="/activity" className="text-sm font-semibold text-neutral-500 hover:text-neutral-900">All activity →</Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {decisions.map(d => <DecisionCard key={d.id} decision={d} />)}
            </div>
          </div>
        )}

        {/* ── PRICE OPPORTUNITIES ─────────────────────────────────────── */}
        {buyNowPrices.length > 0 && (
          <div className="mx-4 md:mx-8 mb-8 bg-green-50 border border-green-100 rounded-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-black text-neutral-900">Price opportunities</h2>
                <p className="text-sm text-neutral-500">These items are below your usual price right now</p>
              </div>
              <Link href="/price-watch" className="text-sm font-semibold text-green-700 hover:underline">Price Watch →</Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {buyNowPrices.map((item: any) => (
                <div key={item.product_id} className="bg-white rounded-2xl p-4 border border-green-100 hover:shadow-sm transition-all">
                  <p className="text-xs font-bold text-neutral-400 uppercase tracking-wider mb-1">{item.brand}</p>
                  <p className="text-sm font-semibold text-neutral-900 mb-2 line-clamp-2">{item.name}</p>
                  <div className="flex items-baseline gap-2 mb-1">
                    <span className="text-lg font-black text-neutral-900">₹{item.current_price}</span>
                    <span className="text-xs text-neutral-400 line-through">₹{item.typical_price}</span>
                  </div>
                  <p className="text-xs text-green-700 font-semibold">{Math.abs(item.price_vs_avg_pct)}% below average</p>
                  <Link href="/nova-cart" className="mt-3 block text-center py-1.5 bg-green-100 hover:bg-green-200 text-green-800 text-xs font-bold rounded-lg transition-colors">Add to NOVA Cart</Link>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── COMMAND BOX ─────────────────────────────────────────────── */}
        <div className="px-4 md:px-8 mb-8">
          <CommandBox />
        </div>

        {/* ── SHOP BY CATEGORY ────────────────────────────────────────── */}
        <div className="px-4 md:px-8 py-8 bg-white mb-8 border-y border-neutral-100">
          <h2 className="text-2xl font-black text-neutral-900 tracking-tight mb-2">Shop by Category</h2>
          <p className="text-sm text-neutral-500 mb-6">Amazon · Demo data</p>
          <div className="mb-8">
            <h3 className="text-sm font-bold text-neutral-500 uppercase tracking-wider mb-4">Groceries & Food</h3>
            <div className="flex flex-wrap gap-4">
              {groceryCats.map((cat, i) => {
                const ext = ["milk","rice","noodles","oil"].includes(cat.key) ? "webp" : "png";
                return (
                  <div key={i} className="flex-shrink-0">
                    <CategoryCard name={cat.name} image={`/assets/fallbacks/${cat.key}.${ext}`} href={`/catalog?category=${cat.name}`} />
                  </div>
                );
              })}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-bold text-neutral-500 uppercase tracking-wider mb-4">Household & Personal Care</h3>
            <div className="flex flex-wrap gap-4">
              {householdCats.map((cat, i) => (
                <div key={i} className="flex-shrink-0">
                  <CategoryCard name={cat.name} image={`/assets/fallbacks/${cat.key || "detergent"}.png`} href={`/catalog?category=${cat.name}`} />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── PRODUCT SHELVES ─────────────────────────────────────────── */}
        <div className="px-4 md:px-8 mb-8 space-y-12">
          <ProductShelf title="NOVA Recommends this month" products={autopilotRecommends} />
        </div>

        <div className="bg-orange-50 px-4 md:px-8 py-10 mb-8 border-y border-orange-100">
          <ProductShelf title="Your Usual Brands" products={usuals} viewAllLink="/catalog" />
        </div>

        <div className="px-4 md:px-8 mb-10 space-y-14">
          {groceries.length > 0 && <ProductShelf title="Grocery Essentials" products={groceries} viewAllLink="/catalog" />}
          {household.length > 0 && <ProductShelf title="Household Supplies" products={household} viewAllLink="/catalog" />}
          {snacks.length > 0 && <ProductShelf title="Snacks & Beverages" products={snacks} viewAllLink="/catalog" />}
        </div>

        {/* ── REMINDER STRIP ──────────────────────────────────────────── */}
        {reminders.length > 0 && (
          <div className="mx-4 md:mx-8 mb-10 bg-blue-50 border border-blue-100 rounded-3xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-black text-neutral-900">Things worth remembering</h2>
              <Link href="/reminders" className="text-sm font-semibold text-blue-700 hover:underline">All reminders →</Link>
            </div>
            <div className="space-y-2">
              {reminders.slice(0, 4).map((rem) => (
                <Link key={rem.id} href={rem.action_url || "/reminders"}
                  className="flex items-center gap-3 p-3 bg-white rounded-xl border border-blue-100 hover:border-blue-300 transition-all group">
                  <div className={`w-2 h-2 rounded-full shrink-0 ${rem.priority === "HIGH" ? "bg-[#FF9900]" : rem.priority === "MEDIUM" ? "bg-blue-400" : "bg-neutral-300"}`}></div>
                  <p className="text-sm text-neutral-800 flex-1">{rem.message}</p>
                  <svg className="text-neutral-300 group-hover:text-neutral-500 transition-colors shrink-0" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Footer spacer */}
        <div className="h-12"></div>
      </div>
    </div>
  );
}
