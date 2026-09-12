"use client";

import { useState, useEffect, useCallback, useRef, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import ProductCard from "@/components/ProductCard";

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

const CATEGORY_TABS = [
  { label: "All Items", key: "all" },
  { label: "Milk & Dairy", key: "milk" },
  { label: "Instant Noodles", key: "noodles" },
  { label: "Cleaning & Toiletries", key: "cleaning" },
  { label: "Cooking Oils", key: "oil" },
  { label: "Atta & Rice", key: "grains" },
  { label: "Tea & Staples", key: "staples" },
];

function CatalogContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const activeCategoryParam = searchParams.get("category") || "all";
  const queryParam = searchParams.get("q") || searchParams.get("query") || "";

  const [activeCategory, setActiveCategory] = useState(activeCategoryParam);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [swiggyStatus, setSwiggyStatus] = useState<{
    authenticated: boolean;
    active_address?: any;
    mode?: string;
  }>({ authenticated: false });

  useEffect(() => {
    fetch("/api/auth/swiggy/status")
      .then((r) => r.json())
      .then((d) => setSwiggyStatus(d))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setActiveCategory(searchParams.get("category") || "all");
  }, [searchParams]);

  useEffect(() => {
    setLoading(true);
    const endpoint = queryParam
      ? `/api/products/search?q=${encodeURIComponent(queryParam)}`
      : `/api/products?limit=100`;

    fetch(endpoint)
      .then((r) => r.json())
      .then((data) => {
        setProducts(Array.isArray(data) ? data : []);
      })
      .catch((err) => {
        console.error("Failed to load catalog products", err);
        setProducts([]);
      })
      .finally(() => setLoading(false));
  }, [queryParam]);

  const handleCategorySelect = (key: string) => {
    setActiveCategory(key);
    if (key === "all") {
      router.push("/catalog");
    } else {
      router.push(`/catalog?category=${encodeURIComponent(key)}`);
    }
  };

  const filtered = products.filter((p) => {
    if (activeCategory === "all") return true;
    const cat = (p.category || "").toLowerCase();
    const name = (p.name || "").toLowerCase();
    if (activeCategory === "milk") return cat.includes("milk") || name.includes("milk");
    if (activeCategory === "noodles") return cat.includes("noodles") || name.includes("maggi") || name.includes("noodle");
    if (activeCategory === "cleaning") return cat.includes("clean") || name.includes("harpic") || name.includes("detergent") || name.includes("soap");
    if (activeCategory === "oil") return cat.includes("oil") || name.includes("oil");
    if (activeCategory === "grains") return cat.includes("rice") || cat.includes("atta") || name.includes("rice") || name.includes("atta");
    if (activeCategory === "staples") return cat.includes("tea") || cat.includes("sugar") || cat.includes("salt") || name.includes("tea");
    return cat.includes(activeCategory.toLowerCase()) || name.includes(activeCategory.toLowerCase());
  });

  return (
    <div className="min-h-screen bg-[#EAEDED] py-5">
      <div className="max-w-[1500px] mx-auto px-4">
        {/* Page Header */}
        <div className="bg-white p-4 rounded-sm border border-neutral-200 mb-4 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-3">
            <div>
              <h1 className="text-xl font-bold text-neutral-900 tracking-tight flex items-center gap-2">
                <span>NOVA Commerce Catalog</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-orange-100 text-[#FC8019]">
                  Swiggy Instamart
                </span>
              </h1>
              <p className="text-xs text-neutral-500 mt-0.5">
                Real-time commerce items via Swiggy Instamart adapter with Household Autopilot intelligence.
              </p>
            </div>
            <div className="text-xs text-neutral-600 bg-neutral-100 px-3 py-1.5 rounded border border-neutral-200 self-start md:self-auto">
              Showing <span className="font-bold text-neutral-900">{filtered.length}</span> products
            </div>
          </div>

          {/* Swiggy Instamart Connection Notice */}
          {swiggyStatus.authenticated ? (
            <div className="flex items-center justify-between bg-emerald-50 border border-emerald-200 px-3 py-2 rounded mb-3 text-xs text-emerald-800">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="font-semibold">Swiggy Instamart Live Session Active</span>
                {swiggyStatus.active_address && (
                  <span className="text-emerald-700 hidden sm:inline">
                    — Delivering to {swiggyStatus.active_address.label || swiggyStatus.active_address.addressCategory || swiggyStatus.active_address.formattedAddress}
                  </span>
                )}
              </div>
              <span className="text-[11px] font-medium bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                Live Product Catalog &amp; Pricing
              </span>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-amber-50 border border-amber-200 p-3 rounded mb-3 text-xs text-amber-900">
              <div className="flex items-center gap-2">
                <span className="text-base">⚠️</span>
                <div>
                  <span className="font-bold">Swiggy Instamart is currently not connected.</span>
                  <p className="text-amber-800 text-[11px] mt-0.5">
                    Connect your Swiggy account with phone &amp; OTP via OAuth 2.1 to fetch real live pricing, local store inventory, and authentic CDN images.
                  </p>
                </div>
              </div>
              <a
                href="/api/auth/swiggy/login?redirect=true"
                className="inline-flex items-center justify-center px-4 py-2 bg-[#FC8019] hover:bg-[#e07014] text-white text-xs font-bold rounded shadow-xs whitespace-nowrap transition-colors"
              >
                Connect Swiggy Instamart
              </a>
            </div>
          )}

          {/* Category Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1 hide-scrollbar">
            {CATEGORY_TABS.map((tab) => {
              const isActive =
                activeCategory === tab.key ||
                (tab.key === "all" && activeCategory === "all");
              return (
                <button
                  key={tab.key}
                  onClick={() => handleCategorySelect(tab.key)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all ${
                    isActive
                      ? "bg-[#131921] text-white shadow-xs"
                      : "bg-[#F0F2F2] text-neutral-700 hover:bg-neutral-200 border border-neutral-300"
                  }`}
                >
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Product Grid */}
        {loading ? (
          <div className="bg-white p-16 rounded-sm border border-neutral-200 text-center">
            <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm font-medium text-neutral-600">Loading catalog items...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-white p-16 rounded-sm border border-neutral-200 text-center">
            <p className="text-base font-bold text-neutral-900 mb-1">
              {!swiggyStatus.authenticated ? "Swiggy Instamart Not Connected" : "No products found in this category"}
            </p>
            <p className="text-xs text-neutral-500 mb-4">
              {!swiggyStatus.authenticated
                ? "Connect your Swiggy Instamart account to load authentic local store inventory and live products."
                : "Select another department to view items."}
            </p>
            {!swiggyStatus.authenticated ? (
              <a
                href="/api/auth/swiggy/login?redirect=true"
                className="inline-block px-5 py-2.5 bg-[#FC8019] hover:bg-[#e07014] text-xs font-bold text-white rounded-md shadow-sm transition-all"
              >
                Connect Swiggy Instamart
              </a>
            ) : (
              <button
                onClick={() => handleCategorySelect("all")}
                className="px-5 py-2 bg-[#FFD814] hover:bg-[#F7CA00] text-xs font-semibold rounded-full text-neutral-900"
              >
                Show All Products
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {filtered.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function CatalogPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#EAEDED] flex items-center justify-center text-sm text-neutral-500">Loading catalog...</div>}>
      <CatalogContent />
    </Suspense>
  );
}
