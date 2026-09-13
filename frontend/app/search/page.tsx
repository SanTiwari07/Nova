"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import ProductCard from "@/components/ProductCard";
import {
  Star,
  Package,
  UtensilsCrossed,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  Clock,
  ShieldCheck
} from "lucide-react";

interface Product {
  id: string;
  name: string;
  brand?: string | null;
  price: number;
  mrp?: number | null;
  currency?: string;
  pack_size?: string | null;
  quantity?: string | null;
  unit?: string | null;
  imageUrl?: string | null;
  image?: string | null;
  category?: string;
  availability?: boolean;
  in_stock?: boolean;
  retailer?: string;
  is_demo?: boolean;
  tags?: string[];
  days_until_needed?: number;
  avg_price?: number;
}

interface HouseholdContext {
  item_name: string;
  category: string;
  quantity: number;
  unit: string;
  daily_consumption: number;
  days_remaining: number;
  status: string;
  urgency: string;
  suggested_action: string;
}

interface PlanItem {
  plan_id: string;
  title: string;
  meal: string;
  description: string;
  components: Array<{ item: string; essential: boolean; category?: string }>;
}

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  const initialCategory = searchParams.get("category") || "All";

  const [products, setProducts] = useState<Product[]>([]);
  const [householdContext, setHouseholdContext] = useState<HouseholdContext | null>(null);
  const [plans, setPlans] = useState<PlanItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory);
  const [categories, setCategories] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<string>("featured");
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/products/categories")
      .then((r) => r.json())
      .then((cats) => setCategories(cats || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    async function fetchSearchResults() {
      setLoading(true);
      setActionSuccess(null);
      try {
        let url = `/api/products?limit=100`;
        if (query.trim()) {
          url = `/api/search?q=${encodeURIComponent(query.trim())}&limit=100`;
        }
        const res = await fetch(url);
        const data = await res.json();

        if (query.trim() && data && !Array.isArray(data)) {
          setProducts(Array.isArray(data.products) ? data.products : []);
          setHouseholdContext(data.household_context || null);
          setPlans(Array.isArray(data.plans) ? data.plans : []);
        } else {
          setProducts(Array.isArray(data) ? data : []);
          setHouseholdContext(null);
          setPlans([]);
        }
      } catch (err) {
        console.error("Search fetch failed", err);
        setProducts([]);
        setHouseholdContext(null);
        setPlans([]);
      } finally {
        setLoading(false);
      }
    }
    fetchSearchResults();
  }, [query]);

  // Handle autonomous replenish action from search
  const handleQuickReplenish = async (itemName: string) => {
    setActionLoading(true);
    setActionSuccess(null);
    try {
      const res = await fetch("/api/command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: `Replenish ${itemName}` }),
      });
      const data = await res.json();
      setActionSuccess(data.response || "NOVA processed the restock request.");
      window.dispatchEvent(new Event("household-updated"));
      window.dispatchEvent(new Event("budget-updated"));
      window.dispatchEvent(new Event("cart-updated"));
    } catch (err) {
      console.error("Replenish action failed:", err);
    } finally {
      setActionLoading(false);
    }
  };

  // Filter and sort
  const filtered = products
    .filter((p) => {
      if (selectedCategory !== "All" && p.category !== selectedCategory) {
        return false;
      }
      return true;
    })
    .sort((a, b) => {
      if (sortBy === "price-low") return a.price - b.price;
      if (sortBy === "price-high") return b.price - a.price;
      return 0;
    });

  return (
    <div className="min-h-screen bg-[#EAEDED] py-4 pt-16 font-sans">
      <div className="max-w-[1500px] mx-auto px-4">
        {/* Breadcrumb & Subheader */}
        <div className="bg-white px-4 py-2.5 rounded-sm border border-neutral-200 mb-4 flex items-center justify-between shadow-xs">
          <div className="text-xs text-neutral-600">
            {loading ? (
              <span>Searching NOVA intelligence &amp; catalog...</span>
            ) : (
              <span>
                {filtered.length} product results for{" "}
                <span className="font-bold text-[#C45500]">
                  &quot;{query || "All Products"}&quot;
                </span>
                {selectedCategory !== "All" && (
                  <span> in <span className="font-semibold text-neutral-900">{selectedCategory}</span></span>
                )}
              </span>
            )}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="text-neutral-500 font-medium">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="border border-neutral-300 rounded bg-[#F0F2F2] px-2 py-1 text-xs outline-none hover:bg-neutral-200 cursor-pointer"
            >
              <option value="featured">Featured</option>
              <option value="price-low">Price: Low to High</option>
              <option value="price-high">Price: High to Low</option>
            </select>
          </div>
        </div>

        {/* ── HOUSEHOLD CONTEXT BANNER ────────────────────────────────────────── */}
        {householdContext && (
          <div className="mb-4 bg-white rounded-xl border border-amber-200/90 p-4 shadow-2xs">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center shrink-0 text-amber-700">
                  <Package className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-amber-800 bg-amber-100 px-2 py-0.5 rounded-full">
                      Pantry State
                    </span>
                    <h2 className="text-base font-bold text-neutral-900">
                      {householdContext.item_name}
                    </h2>
                    <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full ${
                      householdContext.urgency === "URGENT"
                        ? "bg-red-100 text-red-700 border border-red-200"
                        : householdContext.urgency === "UPCOMING"
                        ? "bg-amber-100 text-amber-800 border border-amber-200"
                        : "bg-emerald-100 text-emerald-800 border border-emerald-200"
                    }`}>
                      {householdContext.status === "LOW" ? "Running Low" : "Stock Healthy"}
                    </span>
                  </div>

                  <p className="text-xs text-neutral-600 mt-1">
                    Current pantry stock: <span className="font-bold text-neutral-900">{householdContext.quantity} {householdContext.unit}</span> (approx. <span className="font-bold text-neutral-900">{householdContext.days_remaining} days</span> of supply left at ~{householdContext.daily_consumption} {householdContext.unit}/day).
                  </p>
                  <p className="text-xs font-semibold text-amber-900 mt-0.5">
                    {householdContext.suggested_action}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 self-start sm:self-center shrink-0">
                <Link
                  href="/pantry"
                  className="px-3 py-1.5 rounded-lg border border-neutral-300 bg-white hover:bg-neutral-50 text-xs font-semibold text-neutral-700 transition-colors"
                >
                  View in Pantry
                </Link>
                {householdContext.days_remaining <= 5 && (
                  <button
                    onClick={() => handleQuickReplenish(householdContext.item_name)}
                    disabled={actionLoading}
                    className="px-3.5 py-1.5 rounded-lg bg-[#FF9900] hover:bg-[#e68900] text-xs font-bold text-neutral-900 transition-colors shadow-2xs cursor-pointer disabled:opacity-50"
                  >
                    {actionLoading ? "Processing..." : "Replenish via NOVA"}
                  </button>
                )}
              </div>
            </div>

            {actionSuccess && (
              <div className="mt-3 p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs text-emerald-800 flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span>{actionSuccess}</span>
              </div>
            )}
          </div>
        )}

        {/* ── HOUSEHOLD PLAN BANNER ───────────────────────────────────────────── */}
        {plans.length > 0 && (
          <div className="mb-4 bg-white rounded-xl border border-orange-200/90 p-4 shadow-2xs">
            <div className="flex items-center justify-between gap-3 mb-2">
              <div className="flex items-center gap-2">
                <UtensilsCrossed className="w-4 h-4 text-[#FF9900]" />
                <span className="text-xs font-bold uppercase tracking-wider text-orange-800">
                  Household Meal Plan
                </span>
              </div>
              <Link href="/" className="text-xs text-[#C45500] font-semibold hover:underline">
                View on Today page →
              </Link>
            </div>
            {plans.map((plan) => (
              <div key={plan.plan_id} className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
                <div>
                  <h3 className="text-sm font-bold text-neutral-900">{plan.title}</h3>
                  <div className="flex items-center gap-2 flex-wrap mt-1 text-xs text-neutral-600">
                    <span>Required components:</span>
                    {plan.components.map((c, i) => (
                      <span key={i} className="bg-neutral-100 px-2 py-0.5 rounded text-neutral-800 font-medium">
                        {c.item}
                      </span>
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => handleQuickReplenish(plan.meal)}
                  disabled={actionLoading}
                  className="self-start sm:self-auto px-3.5 py-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 text-white text-xs font-bold transition-colors cursor-pointer disabled:opacity-50"
                >
                  Take Care of It
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-[240px_1fr] gap-4 items-start">
          {/* Filters Sidebar */}
          <aside className="bg-white p-4 rounded-sm border border-neutral-200 space-y-6 text-xs text-neutral-800">
            <div>
              <h3 className="font-bold text-sm text-neutral-900 mb-2">Category</h3>
              <div className="space-y-1.5">
                <button
                  onClick={() => setSelectedCategory("All")}
                  className={`block text-left w-full hover:text-[#C45500] cursor-pointer ${
                    selectedCategory === "All" ? "font-bold text-[#C45500]" : "text-neutral-700"
                  }`}
                >
                  All Categories
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`block text-left w-full hover:text-[#C45500] truncate cursor-pointer ${
                      selectedCategory === cat ? "font-bold text-[#C45500]" : "text-neutral-700"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            <div className="border-t border-neutral-200 pt-4">
              <h3 className="font-bold text-sm text-neutral-900 mb-2">Customer Reviews</h3>
              <div className="space-y-1">
                {[4, 3, 2].map((stars) => (
                  <div key={stars} className="flex items-center gap-1.5 cursor-pointer hover:text-[#C45500]">
                    <div className="flex items-center gap-0.5">
                      {Array.from({ length: 5 }).map((_, i) => (
                        <Star
                          key={i}
                          className={`w-3.5 h-3.5 ${
                            i < stars ? "fill-[#FFA41C] text-[#FFA41C]" : "text-neutral-300"
                          }`}
                        />
                      ))}
                    </div>
                    <span className="text-[11px] text-neutral-600">&amp; Up</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t border-neutral-200 pt-4">
              <h3 className="font-bold text-sm text-neutral-900 mb-2">NOVA Household Intelligence</h3>
              <div className="p-3 bg-amber-50/80 border border-amber-200/60 rounded-lg text-neutral-700">
                <p className="font-semibold text-xs text-neutral-900 mb-1">Autonomous Restock</p>
                <p className="text-[11px] text-neutral-600 leading-relaxed mb-2">
                  NOVA checks live pantry stock, usage velocity, and safety policies before recommending purchases.
                </p>
                <Link
                  href="/activity"
                  className="text-[11px] font-bold text-[#C45500] hover:underline inline-flex items-center gap-1"
                >
                  View Activity Trail →
                </Link>
              </div>
            </div>
          </aside>

          {/* Results Grid */}
          <main>
            {loading ? (
              <div className="bg-white p-12 rounded-sm border border-neutral-200 text-center">
                <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin mx-auto mb-3" />
                <p className="text-sm font-medium text-neutral-600">Querying household database &amp; commerce catalog...</p>
              </div>
            ) : filtered.length === 0 ? (
              <div className="bg-white p-10 rounded-xl border border-neutral-200 text-center">
                <div className="w-12 h-12 rounded-full bg-neutral-100 flex items-center justify-center mx-auto mb-3 text-neutral-400">
                  <Package className="w-6 h-6" />
                </div>
                <h3 className="text-base font-bold text-neutral-900 mb-1">
                  Nothing matched &ldquo;{query}&rdquo;
                </h3>
                <p className="text-xs text-neutral-500 max-w-sm mx-auto mb-5">
                  We couldn&apos;t find an exact catalog match. Try searching for everyday household staples tracked by NOVA:
                </p>
                <div className="flex items-center justify-center gap-2 flex-wrap max-w-md mx-auto">
                  {["Milk", "Fortune Sunflower Oil", "Atta", "Rice", "Tea", "Maggi"].map((staple) => (
                    <button
                      key={staple}
                      onClick={() => router.push(`/search?q=${encodeURIComponent(staple)}`)}
                      className="px-3 py-1 bg-neutral-100 hover:bg-neutral-200 text-xs font-semibold text-neutral-800 rounded-full cursor-pointer transition-colors"
                    >
                      {staple}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {filtered.map((product) => (
                  <ProductCard key={product.id} product={product} />
                ))}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#EAEDED] flex items-center justify-center">Loading search...</div>}>
      <SearchContent />
    </Suspense>
  );
}
