"use client";

import { useState, useEffect, useMemo, useCallback, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import ProductCard from "@/components/ProductCard";
import {
  AlertTriangle,
  CheckCircle2,
  Package,
  RefreshCw,
  Search,
  X,
  Radio,
  SlidersHorizontal,
} from "lucide-react";

export interface Product {
  id: string;
  productId?: string;
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
  imageSource?: string | null;
  imageConfidence?: number | null;
  imageStatus?: string | null;
  barcode?: string | null;
  category?: string;
  availability?: boolean;
  in_stock?: boolean;
  retailer?: string;
  retailerName?: string;
  variantId?: string | null;
  is_demo?: boolean;
  tags?: string[];
  days_until_needed?: number;
  avg_price?: number;
}

const CATEGORY_TABS = [
  { label: "All Items", key: "all" },
  { label: "Milk & Dairy", key: "milk-and-dairy" },
  { label: "Atta & Rice", key: "atta-and-rice" },
  { label: "Cooking Oils", key: "cooking-oils" },
  { label: "Dal & Pulses", key: "dal-and-pulses" },
  { label: "Tea & Staples", key: "tea-and-staples" },
  { label: "Instant Noodles", key: "instant-noodles" },
  { label: "Snacks & Biscuits", key: "snacks-and-biscuits" },
  { label: "Beverages", key: "beverages" },
  { label: "Cleaning & Toiletries", key: "cleaning-and-toiletries" },
  { label: "Personal Care", key: "personal-care" },
];

// Flexible category normalizer for incoming URL params (e.g. ?category=Rice -> atta-and-rice)
function normalizeCategoryKey(param: string | null): string {
  if (!param) return "all";
  const p = param.toLowerCase().trim();
  if (p === "all" || p === "all items") return "all";
  if (p.includes("milk") || p.includes("dairy")) return "milk-and-dairy";
  if (p.includes("atta") || p.includes("flour") || p.includes("rice") || p.includes("grain")) return "atta-and-rice";
  // Check cleaning and toiletries BEFORE oil because 'toiletries' contains 'oil'
  if (p.includes("clean") || p.includes("toilet") || p.includes("detergent") || p.includes("dishwash") || p.includes("laundry") || p.includes("harpic")) return "cleaning-and-toiletries";
  if (p.includes("personal") || p.includes("soap") || p.includes("shampoo") || p.includes("tooth")) return "personal-care";
  if ((p.includes("oil") && !p.includes("toilet")) || p.includes("ghee")) return "cooking-oils";
  if (p.includes("dal") || p.includes("pulse") || p.includes("lentil")) return "dal-and-pulses";
  if (p.includes("tea") || p.includes("coffee") || p.includes("chai") || p.includes("staple") || p.includes("salt") || p.includes("sugar")) return "tea-and-staples";
  if (p.includes("noodle") || p.includes("maggi") || p.includes("pasta")) return "instant-noodles";
  if (p.includes("biscuit") || p.includes("snack") || p.includes("cookie") || p.includes("namkeen") || p.includes("chocolate")) return "snacks-and-biscuits";
  if (p.includes("drink") || p.includes("beverage") || p.includes("juice") || p.includes("soda") || p.includes("pepsi") || p.includes("coke")) return "beverages";
  return "all";
}

type CommerceState =
  | "DISCONNECTED"
  | "CONNECTING"
  | "CONNECTED_LOADING_CATALOG"
  | "CONNECTED_CATALOG_READY"
  | "CONNECTED_CATALOG_EMPTY"
  | "CONNECTION_ERROR"
  | "CATALOG_FETCH_ERROR"
  | "CATALOG_TIMEOUT";

function CatalogContent() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const urlCategory = searchParams.get("category");
  const urlQuery = searchParams.get("q") || searchParams.get("query") || "";

  const [activeCategory, setActiveCategory] = useState<string>(() => normalizeCategoryKey(urlCategory));
  const [searchQuery, setSearchQuery] = useState(urlQuery);
  const [products, setProducts] = useState<Product[]>([]);
  const [commerceState, setCommerceState] = useState<CommerceState>("CONNECTING");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLiveSession, setIsLiveSession] = useState(false);
  const [activeAddress, setActiveAddress] = useState<any>(null);

  // Sync state when URL params change
  useEffect(() => {
    setActiveCategory(normalizeCategoryKey(searchParams.get("category")));
    setSearchQuery(searchParams.get("q") || searchParams.get("query") || "");
  }, [searchParams]);

  // Load catalog & connection status
  const loadCatalog = useCallback(async () => {
    setCommerceState("CONNECTED_LOADING_CATALOG");
    setErrorMessage(null);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 12000);

    try {
      // 1. Fetch connection status
      const statusRes = await fetch("/api/auth/swiggy/status", { signal: controller.signal })
        .then((r) => r.json())
        .catch(() => ({ authenticated: false }));

      const isLive = Boolean(statusRes?.authenticated);
      setIsLiveSession(isLive);
      setActiveAddress(statusRes?.active_address || null);

      // 2. Fetch products
      const prodRes = await fetch("/api/products?limit=250", { signal: controller.signal });
      clearTimeout(timeoutId);

      if (!prodRes.ok) {
        throw new Error(`Catalog service returned HTTP ${prodRes.status}`);
      }

      const data = await prodRes.json();
      const productList = Array.isArray(data) ? data : [];

      setProducts(productList);

      if (!isLive) {
        setCommerceState("DISCONNECTED");
      } else if (productList.length === 0) {
        setCommerceState("CONNECTED_CATALOG_EMPTY");
      } else {
        setCommerceState("CONNECTED_CATALOG_READY");
      }
    } catch (err: any) {
      clearTimeout(timeoutId);
      if (err?.name === "AbortError") {
        setCommerceState("CATALOG_TIMEOUT");
        setErrorMessage("The commerce service timed out. Please retry.");
      } else {
        setCommerceState("CATALOG_FETCH_ERROR");
        setErrorMessage(err?.message || "Failed to load catalog products.");
      }
      setProducts([]);
    }
  }, []);

  useEffect(() => {
    loadCatalog();
  }, [loadCatalog]);

  const handleCategorySelect = (key: string) => {
    setActiveCategory(key);
    const params = new URLSearchParams(searchParams.toString());
    if (key === "all") {
      params.delete("category");
    } else {
      params.set("category", key);
    }
    const queryString = params.toString();
    router.push(queryString ? `/catalog?${queryString}` : "/catalog");
  };

  const handleShowAllProducts = () => {
    setActiveCategory("all");
    setSearchQuery("");
    router.push("/catalog");
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams(searchParams.toString());
    if (searchQuery.trim()) {
      params.set("q", searchQuery.trim());
    } else {
      params.delete("q");
      params.delete("query");
    }
    const queryString = params.toString();
    router.push(queryString ? `/catalog?${queryString}` : "/catalog");
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    const params = new URLSearchParams(searchParams.toString());
    params.delete("q");
    params.delete("query");
    const queryString = params.toString();
    router.push(queryString ? `/catalog?${queryString}` : "/catalog");
  };

  // Filter products by category AND search query (Requirement 15: Search + Category)
  const filtered = useMemo(() => {
    const q = searchQuery.toLowerCase().trim();

    return products.filter((p) => {
      const cat = (p.category || "").toLowerCase();
      const name = (p.name || "").toLowerCase();
      const brand = (p.brand || "").toLowerCase();
      const tags = (p.tags || []).join(" ").toLowerCase();

      // 1. Category Filter
      let matchesCategory = false;
      if (activeCategory === "all") {
        matchesCategory = true;
      } else if (activeCategory === "milk-and-dairy") {
        matchesCategory = cat === "milk & dairy" || cat.includes("dairy");
      } else if (activeCategory === "atta-and-rice") {
        matchesCategory = cat === "atta & rice" || cat.includes("atta") || cat.includes("flour");
      } else if (activeCategory === "cooking-oils") {
        matchesCategory = cat === "cooking oils" || (cat.includes("oil") && !cat.includes("toilet"));
      } else if (activeCategory === "dal-and-pulses") {
        matchesCategory = cat === "dal & pulses" || cat.includes("pulse");
      } else if (activeCategory === "tea-and-staples") {
        matchesCategory = cat === "tea & staples" || cat === "tea & coffee" || cat.includes("staple");
      } else if (activeCategory === "instant-noodles") {
        matchesCategory = cat === "instant noodles" || cat.includes("noodle");
      } else if (activeCategory === "snacks-and-biscuits") {
        matchesCategory = cat === "snacks & biscuits" || cat.includes("biscuit");
      } else if (activeCategory === "beverages") {
        matchesCategory = cat === "beverages" || cat.includes("beverage");
      } else if (activeCategory === "cleaning-and-toiletries") {
        matchesCategory = cat === "cleaning & toiletries" || cat.includes("clean") || cat.includes("detergent") || cat.includes("toilet");
      } else if (activeCategory === "personal-care") {
        matchesCategory = cat === "personal care";
      } else {
        matchesCategory = cat.includes(activeCategory);
      }

      if (!matchesCategory) return false;

      // 2. Search Query Filter
      if (!q) return true;
      return name.includes(q) || brand.includes(q) || cat.includes(q) || tags.includes(q);
    });
  }, [products, activeCategory, searchQuery]);

  return (
    <div className="min-h-screen bg-[#EAEDED] py-5">
      <div className="max-w-[1500px] mx-auto px-4">
        {/* Page Header Card */}
        <div className="bg-white p-4 rounded-sm border border-neutral-200 mb-4 shadow-xs">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-3">
            <div>
              <h1 className="text-xl font-bold text-neutral-900 tracking-tight flex items-center gap-2">
                <span>NOVA Commerce Catalog</span>
                {isLiveSession ? (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-orange-100 text-[#FC8019] flex items-center gap-1">
                    <Radio className="w-3 h-3 text-[#FC8019] animate-pulse" />
                    Swiggy Instamart Live
                  </span>
                ) : (
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-100 text-blue-800 flex items-center gap-1">
                    <Package className="w-3 h-3 text-blue-600" />
                    NOVA Demo Mode
                  </span>
                )}
              </h1>
              <p className="text-xs text-neutral-500 mt-0.5">
                {isLiveSession
                  ? "Real-time commerce items from Swiggy Instamart dark store with Household Autopilot intelligence."
                  : "Verified household replenishment catalog with realistic pricing, inventory context, and Autopilot execution."}
              </p>
            </div>

            {/* Dynamic Product Count */}
            <div className="flex items-center gap-2 self-start md:self-auto">
              <div className="text-xs text-neutral-600 bg-neutral-100 px-3 py-1.5 rounded border border-neutral-200">
                Showing <span className="font-bold text-neutral-900">{filtered.length}</span> products
              </div>
              <button
                onClick={loadCatalog}
                className="p-1.5 text-neutral-500 hover:text-neutral-900 border border-neutral-200 rounded hover:bg-neutral-50 transition-colors"
                title="Refresh catalog"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          {/* Truthful Connection Notice */}
          {commerceState === "CONNECTED_CATALOG_READY" && (
            <div className="flex items-center justify-between bg-emerald-50 border border-emerald-200 px-3 py-2 rounded mb-3 text-xs text-emerald-800">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                <span className="font-semibold">Swiggy Instamart Live Session Active</span>
                {activeAddress && (
                  <span className="text-emerald-700 hidden sm:inline">
                    - Delivering to {activeAddress.label || activeAddress.addressCategory || activeAddress.formattedAddress}
                  </span>
                )}
              </div>
              <span className="text-[11px] font-medium bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded">
                Live Store Inventory
              </span>
            </div>
          )}

          {commerceState === "CONNECTED_CATALOG_EMPTY" && (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-amber-50 border border-amber-300 p-3 rounded mb-3 text-xs text-amber-950">
              <div className="flex items-center gap-2.5">
                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0" />
                <div>
                  <span className="font-bold text-sm">Swiggy Instamart is currently unavailable.</span>
                  <p className="text-amber-800 text-[11px] mt-0.5">
                    Live dark store inventory could not be retrieved from the Swiggy Instamart MCP service. As per real-mode safety rules, NOVA will not silently substitute mock products.
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
                <button
                  onClick={loadCatalog}
                  className="inline-flex items-center gap-1 px-3 py-1.5 bg-[#FC8019] hover:bg-[#e07014] text-white text-xs font-bold rounded shadow-xs transition-colors"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Retry Connection
                </button>
                <button
                  onClick={async () => {
                    await fetch("/api/auth/swiggy/disconnect", { method: "POST" });
                    window.dispatchEvent(new Event("swiggy-updated"));
                    loadCatalog();
                  }}
                  className="inline-flex items-center gap-1 px-3 py-1.5 bg-white border border-neutral-300 hover:bg-neutral-50 text-neutral-800 text-xs font-semibold rounded shadow-xs transition-colors"
                >
                  Switch to Demo Mode
                </button>
              </div>
            </div>
          )}

          {commerceState === "DISCONNECTED" && (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-amber-50 border border-amber-200 p-3 rounded mb-3 text-xs text-amber-900">
              <div className="flex items-center gap-2.5">
                <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
                <div>
                  <span className="font-bold">Swiggy Instamart: Demo Mode Active</span>
                  <p className="text-amber-800 text-[11px] mt-0.5">
                    Showing simulated household items. Connect your Swiggy account to enable live store inventory, real-time pricing, and 10-minute delivery.
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

          {(commerceState === "CATALOG_FETCH_ERROR" || commerceState === "CATALOG_TIMEOUT") && (
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-rose-50 border border-rose-200 p-3 rounded mb-3 text-xs text-rose-900">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
                <div>
                  <span className="font-bold">Failed to load live catalog</span>
                  <p className="text-rose-700 text-[11px] mt-0.5">
                    {errorMessage || "The commerce service encountered an unexpected error."}
                  </p>
                </div>
              </div>
              <button
                onClick={loadCatalog}
                className="inline-flex items-center gap-1 px-4 py-1.5 bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold rounded transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry
              </button>
            </div>
          )}

          {/* Search bar inside catalog */}
          <form onSubmit={handleSearchSubmit} className="flex items-center gap-2 mb-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Filter catalog products by name, brand, or department..."
                className="w-full pl-9 pr-8 py-1.5 text-xs bg-neutral-50 border border-neutral-200 rounded text-neutral-900 outline-none focus:border-neutral-400 focus:bg-white transition-colors"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-700"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
            <button
              type="submit"
              className="px-3 py-1.5 bg-neutral-900 hover:bg-neutral-800 text-white text-xs font-semibold rounded transition-colors"
            >
              Filter
            </button>
          </form>

          {/* Category Filter Pills */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1 hide-scrollbar border-t border-neutral-100 mt-2">
            <SlidersHorizontal className="w-3.5 h-3.5 text-neutral-400 shrink-0 mr-1 hidden sm:block" />
            {CATEGORY_TABS.map((tab) => {
              const isActive = activeCategory === tab.key;
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

        {/* Product Grid / States */}
        {commerceState === "CONNECTED_LOADING_CATALOG" ? (
          <div className="bg-white p-16 rounded-sm border border-neutral-200 text-center">
            <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin mx-auto mb-3" />
            <p className="text-sm font-medium text-neutral-600">Loading catalog items...</p>
          </div>
        ) : commerceState === "CONNECTED_CATALOG_EMPTY" ? (
          <div className="bg-white p-12 sm:p-16 rounded-sm border border-neutral-200 text-center max-w-xl mx-auto my-6 shadow-xs">
            <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <AlertTriangle className="w-6 h-6 text-amber-600" />
            </div>
            <h2 className="text-lg font-bold text-neutral-900 mb-2">
              Swiggy Instamart is currently unavailable.
            </h2>
            <p className="text-xs text-neutral-600 mb-6 leading-relaxed">
              We connected to your Swiggy Instamart profile, but live store inventory could not be loaded from the MCP dark store endpoint. As per real-mode safety policy, simulated products are not silently mixed into real orders.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
              <button
                onClick={loadCatalog}
                className="w-full sm:w-auto px-5 py-2 bg-[#FC8019] hover:bg-[#e07014] text-xs font-bold rounded-full text-white transition-colors shadow-xs flex items-center justify-center gap-1.5"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry Swiggy Connection
              </button>
              <button
                onClick={async () => {
                  await fetch("/api/auth/swiggy/disconnect", { method: "POST" });
                  window.dispatchEvent(new Event("swiggy-updated"));
                  loadCatalog();
                }}
                className="w-full sm:w-auto px-5 py-2 bg-neutral-100 hover:bg-neutral-200 text-xs font-semibold rounded-full text-neutral-800 border border-neutral-300 transition-colors shadow-xs"
              >
                Switch to Demo Catalog
              </button>
            </div>
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-white p-16 rounded-sm border border-neutral-200 text-center">
            <Package className="w-10 h-10 text-neutral-300 mx-auto mb-3" />
            <p className="text-base font-bold text-neutral-900 mb-1">
              No products found in this category
            </p>
            <p className="text-xs text-neutral-500 mb-4">
              {searchQuery
                ? `No products matched "${searchQuery}" in ${CATEGORY_TABS.find((t) => t.key === activeCategory)?.label || "this category"}.`
                : "Select another department to view items, or clear active filters."}
            </p>
            <button
              onClick={handleShowAllProducts}
              className="px-5 py-2 bg-[#FFD814] hover:bg-[#F7CA00] text-xs font-semibold rounded-full text-neutral-900 transition-colors shadow-xs"
            >
              Show All Products
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
            {filtered.map((product) => (
              <ProductCard key={product.id || product.variantId} product={product} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function CatalogPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#EAEDED] flex items-center justify-center text-sm text-neutral-500">
          Loading catalog...
        </div>
      }
    >
      <CatalogContent />
    </Suspense>
  );
}
