"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import ProductCard from "@/components/ProductCard";
import { Star } from "lucide-react";

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

function SearchContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get("q") || "";
  const initialCategory = searchParams.get("category") || "All";

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory);
  const [categories, setCategories] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<string>("featured");
  const [minRating, setMinRating] = useState<number>(0);

  useEffect(() => {
    fetch("/api/products/categories")
      .then((r) => r.json())
      .then((cats) => setCategories(cats || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    async function fetchSearchResults() {
      setLoading(true);
      try {
        let url = `/api/products?limit=100`;
        if (query.trim()) {
          url = `/api/products/search?q=${encodeURIComponent(query.trim())}&limit=100`;
        }
        const res = await fetch(url);
        const data = await res.json();
        setProducts(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Search fetch failed", err);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    }
    fetchSearchResults();
  }, [query]);

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
    <div className="min-h-screen bg-[#EAEDED] py-4">
      <div className="max-w-[1500px] mx-auto px-4">
        {/* Breadcrumb & Subheader */}
        <div className="bg-white px-4 py-2.5 rounded-sm border border-neutral-200 mb-4 flex items-center justify-between shadow-xs">
          <div className="text-xs text-neutral-600">
            {loading ? (
              <span>Searching catalog...</span>
            ) : (
              <span>
                1-{filtered.length} of {products.length} results for{" "}
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

        <div className="grid grid-cols-1 md:grid-cols-[240px_1fr] gap-4 items-start">
          {/* Filters Sidebar */}
          <aside className="bg-white p-4 rounded-sm border border-neutral-200 space-y-6 text-xs text-neutral-800">
            <div>
              <h3 className="font-bold text-sm text-neutral-900 mb-2">Category</h3>
              <div className="space-y-1.5">
                <button
                  onClick={() => setSelectedCategory("All")}
                  className={`block text-left w-full hover:text-[#C45500] ${
                    selectedCategory === "All" ? "font-bold text-[#C45500]" : "text-neutral-700"
                  }`}
                >
                  All Categories
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    className={`block text-left w-full hover:text-[#C45500] truncate ${
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
              <h3 className="font-bold text-sm text-neutral-900 mb-2">NOVA Autopilot</h3>
              <div className="p-3 bg-orange-50 border border-orange-100 rounded-sm text-neutral-700">
                <p className="font-semibold text-xs text-neutral-900 mb-1">Household Sync</p>
                <p className="text-[11px] text-neutral-600 leading-relaxed mb-2">
                  Autopilot monitors your consumption rates and highlights routine essentials.
                </p>
                <Link
                  href="/autopilot"
                  className="text-[11px] font-bold text-[#C45500] hover:underline"
                >
                  Open Autopilot →
                </Link>
              </div>
            </div>
          </aside>

          {/* Results Grid */}
          <main>
            {loading ? (
              <div className="bg-white p-12 rounded-sm border border-neutral-200 text-center">
                <div className="w-8 h-8 border-4 border-neutral-200 border-t-[#FF9900] rounded-full animate-spin mx-auto mb-3" />
                <p className="text-sm font-medium text-neutral-600">Searching NOVA commerce catalog...</p>
              </div>
            ) : filtered.length === 0 ? (
              <div className="bg-white p-12 rounded-sm border border-neutral-200 text-center">
                <p className="text-lg font-bold text-neutral-900 mb-2">No matching products found</p>
                <p className="text-sm text-neutral-500 mb-6">
                  Try checking your spelling or using more general terms like &quot;rice&quot;, &quot;milk&quot;, or &quot;tea&quot;.
                </p>
                <Link
                  href="/catalog"
                  className="px-6 py-2 bg-[#FFD814] hover:bg-[#F7CA00] text-xs font-semibold rounded-full text-neutral-900 inline-block"
                >
                  Browse Full Catalog
                </Link>
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
