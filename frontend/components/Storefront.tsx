"use client";

import { useState, useEffect, useRef, useMemo } from "react";
import Link from "next/link";
import ProductShelf from "@/components/ProductShelf";
import CategoryCard from "@/components/CategoryCard";
import CommandBox from "@/components/CommandBox";
import {
  Zap,
  Sparkles,
  ShieldCheck,
  AlertCircle,
  Package,
  Utensils,
  Droplet,
  Coffee,
  Sun,
  Cookie,
  CupSoda,
  Lightbulb,
  X,
  CheckCircle2,
  Check,
  Milk,
  Layers,
  ArrowRight,
  RefreshCw,
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
  rating?: number;
  review_count?: number;
}

const HERO_SLIDES = [
  {
    id: 1,
    badge: "Household Autopilot Active",
    icon: "zap",
    title: "NOVA Super Value Days",
    subtitle: "Up to 35% off on Groceries & Monthly Staples",
    detail: "Atta, Basmati Rice, Cooking Oils & Daily Essentials delivered next-day.",
    cta: "Shop Daily Deals",
    href: "/catalog?category=Rice",
    bgGradient: "from-[#FDE68A] via-[#FBBF24] to-[#F59E0B]",
  },
  {
    id: 2,
    badge: "Pantry Restock Alert",
    icon: "alert",
    title: "Never Run Out of Morning Tea & Fresh Milk",
    subtitle: "Amul, Tata Tea, Nescafe & Kellogg's Breakfast Essentials",
    detail: "NOVA predicts depletion before you wake up to an empty carton.",
    cta: "Explore Breakfast",
    href: "/catalog?category=Tea",
    bgGradient: "from-[#BAE6FD] via-[#7DD3FC] to-[#38BDF8]",
  },
  {
    id: 3,
    badge: "Budget-Safe Autonomous Shopping",
    icon: "shield",
    title: "Home Care & Cleaning Essentials",
    subtitle: "Surf Excel, Vim, Dettol & Harpic",
    detail: "Automatic orders respect your ₹5,000 monthly household budget limit.",
    cta: "Shop Cleaners",
    href: "/catalog?category=Detergent",
    bgGradient: "from-[#BBF7D0] via-[#86EFAC] to-[#4ADE80]",
  },
];

const GROCERY_CATEGORIES = [
  { name: "Atta & Flour", key: "atta", href: "/catalog?category=Atta%20%26%20Rice" },
  { name: "Basmati Rice", key: "rice", href: "/catalog?category=Atta%20%26%20Rice" },
  { name: "Dals & Pulses", key: "dal", href: "/catalog?category=Dal%20%26%20Pulses" },
  { name: "Cooking Oils", key: "oil", href: "/catalog?category=Cooking%20Oils" },
  { name: "Milk & Dairy", key: "milk", href: "/catalog?category=Milk%20%26%20Dairy" },
  { name: "Tea & Chai", key: "tea", href: "/catalog?category=Tea%20%26%20Staples" },
  { name: "Coffee", key: "coffee", href: "/catalog?category=Tea%20%26%20Staples" },
  { name: "Instant Noodles", key: "noodles", href: "/catalog?category=Instant%20Noodles" },
  { name: "Biscuits", key: "biscuits", href: "/catalog?category=Snacks%20%26%20Biscuits" },
  { name: "Cold Drinks", key: "drinks", href: "/catalog?category=Beverages" },
  { name: "Chocolates", key: "chocolates", href: "/catalog?category=Snacks%20%26%20Biscuits" },
  { name: "Cleaning", key: "cleaning", href: "/catalog?category=Cleaning%20%26%20Toiletries" },
];

export default function Storefront() {
  const [products, setProducts] = useState<Product[]>([]);
  const [sections, setSections] = useState<Record<string, Product[]> | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentSlide, setCurrentSlide] = useState(0);
  const [budget, setBudget] = useState<{ monthly: number; spent: number; remaining: number; auto_limit: number } | null>(null);
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [prodRes, secRes, budRes, statRes] = await Promise.all([
          fetch("/api/products?limit=250").then((r) => r.json()).catch(() => []),
          fetch("/api/products/sections").then((r) => r.json()).catch(() => null),
          fetch("/api/budget").then((r) => r.json()).catch(() => null),
          fetch("/api/household-status").then((r) => r.json()).catch(() => null),
        ]);
        setProducts(Array.isArray(prodRes) ? prodRes : []);
        setSections(secRes && typeof secRes === "object" ? secRes : null);
        setBudget(budRes);
        setStatus(statRes);
      } catch (err) {
        console.error("Failed to load storefront data", err);
      } finally {
        setLoading(false);
      }
    }
    loadInitialData();

    const handleUpdate = () => {
      loadInitialData();
    };
    window.addEventListener("household-updated", handleUpdate);
    window.addEventListener("cart-updated", handleUpdate);
    return () => {
      window.removeEventListener("household-updated", handleUpdate);
      window.removeEventListener("cart-updated", handleUpdate);
    };
  }, []);

  // Slide auto-rotation
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % HERO_SLIDES.length);
    }, 6000);
    return () => clearInterval(timer);
  }, []);

  // Filter specific product sets for shelves strictly by canonical category.
  // Never cross-contaminate shelves with unrelated categories.
  // Never fallback to arbitrary slices.
  const deals = useMemo(() => {
    if (sections?.deals?.length) return sections.deals;
    if (!products.length) return [];
    const seenCats = new Set<string>();
    const selected: Product[] = [];
    for (const p of products) {
      if (p.category && !seenCats.has(p.category)) {
        seenCats.add(p.category);
        selected.push(p);
      }
    }
    for (const p of products) {
      if (selected.length >= 10) break;
      if (!selected.some((x) => x.id === p.id)) {
        selected.push(p);
      }
    }
    return selected.map((p) => ({
      ...p,
      tags: p.tags ? Array.from(new Set([...p.tags, "deal"])) : ["deal"],
    }));
  }, [sections, products]);

  const usuals = useMemo(() => {
    if (sections?.usuals?.length) return sections.usuals;
    if (!products.length) return [];
    return products
      .filter((p) =>
        ["Milk & Dairy", "Tea & Staples", "Tea & Coffee", "Atta & Rice", "Cooking Oils"].includes(p.category || "")
      )
      .slice(0, 10)
      .map((p) => ({
        ...p,
        tags: p.tags ? Array.from(new Set([...p.tags, "usual"])) : ["usual"],
      }));
  }, [sections, products]);

  const groceries = useMemo(() => {
    if (sections?.groceries?.length) return sections.groceries;
    if (!products.length) return [];
    return products
      .filter((p) =>
        ["Atta & Rice", "Cooking Oils", "Dal & Pulses", "Tea & Staples"].includes(p.category || "")
      )
      .slice(0, 10);
  }, [sections, products]);

  const household = useMemo(() => {
    if (sections?.household?.length) return sections.household;
    if (!products.length) return [];
    // Strict cleaning & toiletries / personal care only. Zero food/milk/tea.
    return products
      .filter((p) => p.category === "Cleaning & Toiletries" || p.category === "Personal Care")
      .slice(0, 10);
  }, [sections, products]);

  const snacks = useMemo(() => {
    if (sections?.snacks?.length) return sections.snacks;
    if (!products.length) return [];
    // Strict snacks, biscuits, instant noodles, beverages only. Zero cleaning/tea/oils.
    return products
      .filter((p) => p.category === "Snacks & Biscuits" || p.category === "Instant Noodles" || p.category === "Beverages")
      .slice(0, 10);
  }, [sections, products]);

  const scrollToTop = () => {
    if (typeof window !== "undefined") {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#EAEDED] flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-[#FF9900] animate-spin mx-auto mb-3" />
          <p className="text-sm font-medium text-neutral-600">Loading NOVA Commerce Storefront...</p>
        </div>
      </div>
    );
  }

  const slide = HERO_SLIDES[currentSlide];

  return (
    <div className="min-h-screen bg-[#EAEDED] text-neutral-900 font-sans">
      {/* ── 1. PROMOTIONAL COMMERCE HERO CAROUSEL ─────────────────────────── */}
      <div className="relative w-full max-w-[1500px] mx-auto overflow-hidden">
        <div
          className={`w-full transition-all duration-700 bg-gradient-to-r ${slide.bgGradient} px-6 md:px-12 pt-8 pb-36 md:pb-44 flex flex-col justify-between`}
        >
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-black/10 text-neutral-900 text-[11px] font-bold tracking-wide uppercase mb-3 backdrop-blur-xs">
              {slide.icon === "zap" && <Zap className="w-3.5 h-3.5" />}
              {slide.icon === "alert" && <AlertCircle className="w-3.5 h-3.5" />}
              {slide.icon === "shield" && <ShieldCheck className="w-3.5 h-3.5" />}
              {slide.badge}
            </div>
            <h1 className="text-3xl md:text-5xl font-black text-neutral-900 tracking-tight leading-tight mb-2">
              {slide.title}
            </h1>
            <p className="text-base md:text-xl font-semibold text-neutral-800 mb-2">
              {slide.subtitle}
            </p>
            <p className="text-xs md:text-sm text-neutral-700 max-w-xl mb-5">
              {slide.detail}
            </p>
            <Link
              href={slide.href}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#131921] hover:bg-[#232F3E] text-white text-xs font-bold rounded shadow-md transition-all hover:translate-x-0.5"
            >
              {slide.cta} &rarr;
            </Link>
          </div>

          {/* Carousel dots */}
          <div className="absolute top-6 right-6 flex items-center gap-1.5 z-20">
            {HERO_SLIDES.map((s, idx) => (
              <button
                key={s.id}
                onClick={() => setCurrentSlide(idx)}
                className={`w-2.5 h-2.5 rounded-full transition-all ${
                  currentSlide === idx ? "bg-[#131921] w-6" : "bg-black/20 hover:bg-black/40"
                }`}
                aria-label={`Slide ${idx + 1}`}
              />
            ))}
          </div>
        </div>

        {/* ── 2. SIGNATURE 4-UP FEATURE CARDS OVERLAPPING BANNER ──── */}
        <div className="relative -mt-24 md:-mt-32 px-4 z-20 mb-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Box 1: Restock Essentials */}
            <div className="bg-white p-4 rounded-sm border border-neutral-200 shadow-sm flex flex-col justify-between">
              <div>
                <h2 className="text-base font-bold text-neutral-900 mb-3">
                  Household Essentials | Restock
                </h2>
                <div className="grid grid-cols-2 gap-2 mb-3">
                  {[
                    { name: "Atta & Flour", href: "/catalog?category=Atta%20%26%20Rice", icon: Package, color: "bg-amber-50 text-amber-700 border-amber-100" },
                    { name: "Basmati Rice", href: "/catalog?category=Atta%20%26%20Rice", icon: Utensils, color: "bg-emerald-50 text-emerald-700 border-emerald-100" },
                    { name: "Cooking Oils", href: "/catalog?category=Cooking%20Oils", icon: Droplet, color: "bg-yellow-50 text-yellow-700 border-yellow-100" },
                    { name: "Dals & Pulses", href: "/catalog?category=Dal%20%26%20Pulses", icon: Layers, color: "bg-orange-50 text-orange-700 border-orange-100" },
                  ].map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className="group flex flex-col items-center text-center p-2 rounded-lg border border-neutral-100 hover:border-neutral-300 hover:bg-neutral-50 transition-all"
                      >
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-1.5 border ${item.color} group-hover:scale-105 transition-transform`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <span className="text-[11px] font-semibold text-neutral-700 group-hover:text-[#C7511F] truncate w-full">
                          {item.name}
                        </span>
                      </Link>
                    );
                  })}
                </div>
              </div>
              <Link
                href="/catalog?category=Atta%20%26%20Rice"
                className="text-xs font-semibold text-[#007185] hover:text-[#C7511F] hover:underline"
              >
                See all groceries &rarr;
              </Link>
            </div>

            {/* Box 2: NOVA Autopilot Routine Picks */}
            <div className="bg-white p-4 rounded-sm border border-neutral-200 shadow-sm flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-base font-bold text-neutral-900">
                    NOVA Autopilot | Predictions
                  </h2>
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                </div>
                <div className="grid grid-cols-2 gap-2 mb-3">
                  {[
                    { name: "Amul Milk 1L", tag: "Due Tomorrow", color: "bg-red-50 text-red-700", icon: Milk, boxColor: "bg-blue-50 text-blue-700 border-blue-100", productId: "prod_000109" },
                    { name: "Tata Tea 500g", tag: "Due in 5d", color: "bg-orange-50 text-orange-700", icon: Coffee, boxColor: "bg-amber-50 text-amber-700 border-amber-100", productId: "prod_000080" },
                    { name: "Cooking Oil 1L", tag: "Stock Good", color: "bg-green-50 text-green-700", icon: Sun, boxColor: "bg-yellow-50 text-yellow-700 border-yellow-100", productId: "prod_000031" },
                    { name: "Surf Excel 1kg", tag: "Due in 8d", color: "bg-blue-50 text-blue-700", icon: Sparkles, boxColor: "bg-cyan-50 text-cyan-700 border-cyan-100", productId: "prod_000091" },
                  ].map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.name}
                        href={`/catalog/${item.productId}`}
                        className="group flex flex-col items-center text-center p-2 rounded-lg border border-neutral-100 hover:border-neutral-300 hover:bg-neutral-50 cursor-pointer transition-all"
                      >
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-1.5 border ${item.boxColor} group-hover:scale-105 transition-transform`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <span className="text-[11px] font-semibold text-neutral-800 truncate w-full group-hover:text-[#C7511F]">
                          {item.name}
                        </span>
                        <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded-full mt-1 ${item.color}`}>
                          {item.tag}
                        </span>
                      </Link>
                    );
                  })}
                </div>
              </div>
              <Link
                href="/autopilot"
                className="text-xs font-semibold text-[#007185] hover:text-[#C7511F] hover:underline"
              >
                Manage household plan &rarr;
              </Link>
            </div>

            {/* Box 3: Snacks & Beverages */}
            <div className="bg-white p-4 rounded-sm border border-neutral-200 shadow-sm flex flex-col justify-between">
              <div>
                <h2 className="text-base font-bold text-neutral-900 mb-3">
                  Up to 40% off | Daily Snacks
                </h2>
                <div className="grid grid-cols-2 gap-2 mb-3">
                  {[
                    { name: "Biscuits", href: "/catalog?category=Snacks%20%26%20Biscuits", icon: Cookie, color: "bg-amber-50 text-amber-700 border-amber-100" },
                    { name: "Noodles", href: "/catalog?category=Instant%20Noodles", icon: Utensils, color: "bg-orange-50 text-orange-700 border-orange-100" },
                    { name: "Chocolates", href: "/catalog?category=Snacks%20%26%20Biscuits", icon: Package, color: "bg-rose-50 text-rose-700 border-rose-100" },
                    { name: "Cold Drinks", href: "/catalog?category=Beverages", icon: CupSoda, color: "bg-emerald-50 text-emerald-700 border-emerald-100" },
                  ].map((item) => {
                    const Icon = item.icon;
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className="group flex flex-col items-center text-center p-2 rounded-lg border border-neutral-100 hover:border-neutral-300 hover:bg-neutral-50 transition-all"
                      >
                        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-1.5 border ${item.color} group-hover:scale-105 transition-transform`}>
                          <Icon className="w-6 h-6" />
                        </div>
                        <span className="text-[11px] font-semibold text-neutral-700 group-hover:text-[#C7511F] truncate w-full">
                          {item.name}
                        </span>
                      </Link>
                    );
                  })}
                </div>
              </div>
              <Link
                href="/catalog?category=Snacks%20%26%20Biscuits"
                className="text-xs font-semibold text-[#007185] hover:text-[#C7511F] hover:underline"
              >
                See all snacks &amp; drinks &rarr;
              </Link>
            </div>

            {/* Box 4: Household Budget & Policy */}
            <div className="bg-white p-4 rounded-sm border border-neutral-200 shadow-sm flex flex-col justify-between">
              <div>
                <h2 className="text-base font-bold text-neutral-900 mb-3">
                  Household Budget &amp; Safety
                </h2>
                <div className="space-y-2 mb-4 text-xs">
                  <div className="p-2.5 bg-neutral-50 rounded border border-neutral-100 flex justify-between items-center">
                    <span className="text-neutral-500">Monthly Budget:</span>
                    <span className="font-bold text-neutral-900">
                      ₹{(budget?.monthly || 5000).toLocaleString("en-IN")}
                    </span>
                  </div>
                  <div className="p-2.5 bg-green-50 rounded border border-green-100 flex justify-between items-center">
                    <span className="text-green-700 font-medium">Remaining:</span>
                    <span className="font-black text-green-800 text-sm">
                      ₹{(budget?.remaining || 1580).toLocaleString("en-IN")}
                    </span>
                  </div>
                  <div className="p-2.5 bg-orange-50 rounded border border-orange-100 flex justify-between items-center">
                    <span className="text-orange-800 font-medium">Auto Limit per Item:</span>
                    <span className="font-bold text-orange-900">
                      ₹{(budget?.auto_limit || 500).toLocaleString("en-IN")}
                    </span>
                  </div>
                </div>
              </div>
              <Link
                href="/budget"
                className="text-xs font-semibold text-[#007185] hover:text-[#C7511F] hover:underline"
              >
                Manage budget &amp; limits &rarr;
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* ── 3. NOVA AUTONOMOUS HOUSEHOLD COPILOT (AWS STRANDS AGENT) ──────── */}
      <div className="max-w-[1500px] mx-auto px-4 mb-6">
        <CommandBox />
      </div>

      {/* ── 4. CONTEXTUAL NOVA ASSISTANT BANNER ─────────────────────────────── */}
      <div className="max-w-[1500px] mx-auto px-4 mb-8">
        <div className="bg-[#FFFDF9] border-l-4 border-l-[#FF9900] border border-neutral-200 rounded-sm p-4 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="w-8 h-8 rounded-full bg-[#FF9900]/15 flex items-center justify-center text-[#FF9900] shrink-0">
              <Lightbulb className="w-4 h-4 text-[#FF9900]" />
            </div>
            <div>
              <p className="text-xs font-bold text-neutral-900">
                NOVA Household Intelligence: Your pantry stock is healthy
              </p>
              <p className="text-xs text-neutral-600 mt-0.5">
                Amul Taaza Milk is predicted to deplete tomorrow. 2 other routine essentials are within your ₹500 auto-purchase limit.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0 self-end md:self-auto">
            <Link
              href="/autopilot"
              className="px-3.5 py-1.5 bg-[#FFD814] hover:bg-[#F7CA00] text-neutral-900 text-xs font-semibold rounded-full shadow-xs transition-colors"
            >
              Review Autopilot Cart
            </Link>
            <Link
              href="/nova-cart"
              className="px-3.5 py-1.5 bg-white border border-neutral-300 hover:bg-neutral-50 text-neutral-800 text-xs font-semibold rounded-full shadow-xs transition-colors"
            >
              NOVA Cart &rarr;
            </Link>
          </div>
        </div>
      </div>

      {/* ── 5. SHOP BY CATEGORY CIRCLES ───────────────────────────────────── */}
      <div className="max-w-[1500px] mx-auto px-4 mb-8">
        <div className="bg-white p-6 rounded-sm border border-neutral-200 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-bold text-neutral-900 tracking-tight">
              Explore by Category
            </h2>
            <Link
              href="/catalog"
              className="text-xs font-semibold text-[#007185] hover:text-[#C7511F] hover:underline"
            >
              View all categories &rarr;
            </Link>
          </div>
          <div className="flex gap-4 overflow-x-auto pb-2 hide-scrollbar">
            {GROCERY_CATEGORIES.map((cat) => (
              <div key={cat.name} className="shrink-0">
                <CategoryCard
                  name={cat.name}
                  categoryKey={cat.key}
                  href={cat.href}
                />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── 6. DEALS OF THE DAY SHELF ─────────────────────────────────────── */}
      {deals.length > 0 && (
        <div className="max-w-[1500px] mx-auto px-4 mb-8">
          <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs">
            <ProductShelf
              title="Deals of the Day | Grocery &amp; Essentials"
              products={deals}
              viewAllLink="/catalog"
            />
          </div>
        </div>
      )}

      {/* ── 7. YOUR USUAL BRANDS SHELF ────────────────────────────────────── */}
      {usuals.length > 0 && (
        <div className="max-w-[1500px] mx-auto px-4 mb-8">
          <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs">
            <ProductShelf
              title="Frequently Purchased by Your Household"
              products={usuals}
              viewAllLink="/catalog?category=Milk%20%26%20Dairy"
            />
          </div>
        </div>
      )}

      {/* ── 8. GROCERIES & COOKING STAPLES ─────────────────────────────────── */}
      {groceries.length > 0 && (
        <div className="max-w-[1500px] mx-auto px-4 mb-8">
          <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs">
            <ProductShelf
              title="Kitchen &amp; Cooking Staples"
              products={groceries}
              viewAllLink="/catalog?category=Atta%20%26%20Rice"
            />
          </div>
        </div>
      )}

      {/* ── 9. HOUSEHOLD & PERSONAL CARE ───────────────────────────────────── */}
      {household.length > 0 && (
        <div className="max-w-[1500px] mx-auto px-4 mb-10">
          <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs">
            <ProductShelf
              title="Household Cleaning &amp; Laundry"
              products={household}
              viewAllLink="/catalog?category=Cleaning%20%26%20Toiletries"
            />
          </div>
        </div>
      )}

      {/* ── 10. SNACKS & BEVERAGES ────────────────────────────────────────── */}
      {snacks.length > 0 && (
        <div className="max-w-[1500px] mx-auto px-4 mb-12">
          <div className="bg-white p-5 rounded-sm border border-neutral-200 shadow-xs">
            <ProductShelf
              title="Snacks, Biscuits &amp; Beverages"
              products={snacks}
              viewAllLink="/catalog?category=Snacks%20%26%20Biscuits"
            />
          </div>
        </div>
      )}

      {/* Empty State Fallback if no products loaded */}
      {!loading && products.length === 0 && (
        <div className="max-w-[1500px] mx-auto px-4 mb-12">
          <div className="bg-white p-8 rounded-sm border border-neutral-200 shadow-xs text-center">
            <Package className="w-12 h-12 text-neutral-400 mx-auto mb-3" />
            <h3 className="text-base font-bold text-neutral-800 mb-1">Catalog Ready to Connect</h3>
            <p className="text-xs text-neutral-500 mb-4 max-w-md mx-auto">
              Connect your Swiggy Instamart session or browse the catalog to populate household shelves.
            </p>
            <Link
              href="/catalog"
              className="inline-flex items-center gap-2 px-4 py-2 bg-[#FFD814] hover:bg-[#F7CA00] text-neutral-900 text-xs font-semibold rounded-md shadow-xs"
            >
              Open Catalog &rarr;
            </Link>
          </div>
        </div>
      )}

      {/* ── 11. COMMERCE FOOTER ───────────────────────────────────────────── */}
      <footer className="w-full bg-[#232F3E] text-white pt-6">
        <button
          onClick={scrollToTop}
          className="w-full py-3 bg-[#37475A] hover:bg-[#485769] text-xs font-semibold text-center transition-colors block"
        >
          Back to top
        </button>

        <div className="max-w-[1200px] mx-auto px-6 py-12 grid grid-cols-2 md:grid-cols-4 gap-8 text-xs">
          <div>
            <h3 className="font-bold text-sm text-white mb-3">Get to Know Us</h3>
            <ul className="space-y-2 text-neutral-300">
              <li><span className="hover:underline cursor-pointer">About NOVA</span></li>
              <li><span className="hover:underline cursor-pointer">Careers</span></li>
              <li><span className="hover:underline cursor-pointer">Press Releases</span></li>
              <li><span className="hover:underline cursor-pointer">NOVA Science</span></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-sm text-white mb-3">Connect with Us</h3>
            <ul className="space-y-2 text-neutral-300">
              <li><span className="hover:underline cursor-pointer">Twitter / X</span></li>
              <li><span className="hover:underline cursor-pointer">Instagram</span></li>
              <li><span className="hover:underline cursor-pointer">GitHub Hackathon</span></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-sm text-white mb-3">Household Autopilot</h3>
            <ul className="space-y-2 text-neutral-300">
              <li><Link href="/autopilot" className="hover:underline">Autonomous Decision Engine</Link></li>
              <li><Link href="/budget" className="hover:underline">Budget Protection &amp; Rules</Link></li>
              <li><Link href="/pantry" className="hover:underline">Pantry Stock Reconciliation</Link></li>
              <li><Link href="/activity" className="hover:underline">Audit Trail &amp; Transparency</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-bold text-sm text-white mb-3">Let Us Help You</h3>
            <ul className="space-y-2 text-neutral-300">
              <li><Link href="/orders" className="hover:underline">Your Orders</Link></li>
              <li><Link href="/cart" className="hover:underline">Your Shopping Cart</Link></li>
              <li><Link href="/reminders" className="hover:underline">Household Reminders</Link></li>
              <li><span className="hover:underline cursor-pointer">Help Center</span></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-white/10 bg-[#131921] py-6 text-center text-[11px] text-neutral-400">
          <div className="flex items-center justify-center gap-1 font-black text-white text-lg mb-2">
            <span className="text-[#FF9900]">N</span>OVA
          </div>
          <p>© 2026 NOVA Commerce Technologies. Household Autopilot Layer Active.</p>
          <p className="mt-1 text-neutral-500">
            Commerce integration for Household Decision Agent demonstration.
          </p>
        </div>
      </footer>
    </div>
  );
}
