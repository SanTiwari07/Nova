"use client";
import Link from "next/link";
import { useState, useEffect, useRef } from "react";
import ProductImage from "./ProductImage";

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
  variantId?: string | null;
  is_demo?: boolean;
  tags?: string[];
  days_until_needed?: number;
  avg_price?: number;
}

export default function ProductCard({ product }: { product: Product }) {
  const [added, setAdded] = useState(false);
  const [adding, setAdding] = useState(false);

  // ── Async image resolution ──────────────────────────────────────────────────
  // Commerce data (price, availability, name) renders immediately from Swiggy.
  // If no imageUrl was provided by Swiggy, we resolve it asynchronously from
  // Open Food Facts via the ImageResolver pipeline.
  const initialImageUrl = product.imageUrl || product.image || null;
  const initialStatus = product.imageStatus || (initialImageUrl ? "found" : "pending");

  const [resolvedImageUrl, setResolvedImageUrl] = useState<string | null>(initialImageUrl);
  const [imageSource, setImageSource] = useState<string | null>(product.imageSource || null);
  const [imageResolving, setImageResolving] = useState(initialStatus === "pending" && !initialImageUrl);
  const resolveAttempted = useRef(false);

  useEffect(() => {
    // Reset if product changes
    const newUrl = product.imageUrl || product.image || null;
    setResolvedImageUrl(newUrl);
    setImageSource(product.imageSource || (newUrl ? "swiggy" : null));
    const newStatus = product.imageStatus || (newUrl ? "found" : "pending");
    setImageResolving(newStatus === "pending" && !newUrl);
    resolveAttempted.current = false;
  }, [product.id, product.imageUrl, product.image]);

  useEffect(() => {
    // Only attempt resolution if image is genuinely missing
    if (resolvedImageUrl || resolveAttempted.current || !imageResolving) return;
    resolveAttempted.current = true;

    const productKey = product.variantId
      ? `swiggy:${product.variantId}`
      : `swiggy:${product.id}`;

    fetch("/api/images/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        product_key: productKey,
        name: product.name,
        brand: product.brand || null,
        quantity: product.quantity || null,
        unit: product.unit || null,
        pack_size: product.pack_size || null,
        barcode: product.barcode || null,
        swiggy_image_url: null,
      }),
    })
      .then((r) => r.json())
      .then((data: { imageUrl?: string | null; imageSource?: string; imageStatus?: string }) => {
        if (data.imageUrl) {
          setResolvedImageUrl(data.imageUrl);
          setImageSource(data.imageSource || "open_food_facts");
        } else {
          setResolvedImageUrl(null);
          setImageSource("unavailable");
        }
      })
      .catch(() => {
        // Network error: commerce data must continue working; image unavailable
        setResolvedImageUrl(null);
        setImageSource("unavailable");
      })
      .finally(() => setImageResolving(false));
  }, [imageResolving, resolvedImageUrl, product]);

  // ── Commerce data ───────────────────────────────────────────────────────────
  const isAvailable = product.availability ?? product.in_stock ?? true;
  const price = product.price;
  const mrp = product.mrp && product.mrp > price ? product.mrp : null;
  const discountPct = mrp ? Math.round(((mrp - price) / mrp) * 100) : 0;
  const packSize = product.pack_size || (product.quantity && product.unit ? `${product.quantity} ${product.unit}` : null);
  const isDemo = product.is_demo ?? true;

  const handleAddToCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (adding) return;
    setAdding(true);
    try {
      await fetch("/api/cart/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: product.id, quantity: 1 }),
      });
      setAdded(true);
      if (typeof window !== "undefined") {
        window.dispatchEvent(new Event("cart-updated"));
      }
      setTimeout(() => setAdded(false), 2200);
    } catch (err) {
      console.error("Failed to add to cart", err);
    } finally {
      setAdding(false);
    }
  };


  return (
    <div className="group relative flex flex-col h-full bg-white border border-neutral-200 rounded-md p-3 hover:shadow-md transition-all duration-200">
      {/* Retailer & Demo Status Badge */}
      <div className="flex items-center justify-between gap-1 mb-2">
        <span className="text-[10px] font-bold text-[#FC8019] uppercase tracking-wide flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-[#FC8019]"></span>
          Swiggy Instamart
        </span>
        {isDemo ? (
          <span className="px-1.5 py-0.5 bg-amber-50 text-amber-700 border border-amber-200 text-[9px] font-bold rounded">
            SIMULATED
          </span>
        ) : (
          <span className="px-1.5 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 text-[9px] font-bold rounded flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            Live MCP
          </span>
        )}
      </div>

      {/* Product Image — uses async-resolved real URL (never emoji, never AI) */}
      <Link href={`/catalog/${product.id}`} className="block relative w-full aspect-square mb-2 overflow-hidden bg-neutral-50/50 rounded">
        {imageResolving ? (
          /* Skeleton pulse while image resolution is in progress */
          <div className="absolute inset-0 bg-neutral-100 animate-pulse rounded flex items-center justify-center">
            <div className="w-6 h-6 border-2 border-neutral-300 border-t-[#FC8019] rounded-full animate-spin" />
          </div>
        ) : (
          <ProductImage
            src={resolvedImageUrl}
            alt={product.name}
            category={product.category}
            id={product.id}
            imageSource={imageSource}
            fill
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 25vw"
            className="group-hover:scale-105 transition-transform duration-200 object-contain p-2"
          />
        )}
        {/* Image source badge — development observability */}
        {imageSource && imageSource !== "unavailable" && (
          <span className="absolute bottom-1 right-1 text-[8px] font-bold px-1 py-0.5 rounded bg-black/30 text-white pointer-events-none select-none">
            {imageSource === "swiggy" ? "Swiggy" : imageSource === "open_food_facts" ? "OFF" : imageSource}
          </span>
        )}
      </Link>

      {/* Product Information */}
      <div className="flex flex-col flex-grow">
        {/* Brand & Pack size */}
        <div className="flex items-center gap-1 text-[11px] text-neutral-500 mb-0.5 font-medium">
          {product.brand && (
            <span className="text-neutral-700 font-semibold truncate">
              {product.brand}
            </span>
          )}
          {product.brand && packSize && <span>•</span>}
          {packSize && (
            <span className="truncate">{packSize}</span>
          )}
        </div>

        {/* Product Title */}
        <Link
          href={`/catalog/${product.id}`}
          className="text-xs font-semibold text-neutral-900 line-clamp-2 leading-snug hover:text-[#FC8019] mb-1.5 min-h-[32px]"
          title={product.name}
        >
          {product.name}
        </Link>

        {/* Availability Status */}
        <div className="mb-2">
          {isAvailable ? (
            <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-emerald-700">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              In Stock (10-15 min delivery)
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-[10px] font-medium text-rose-600">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
              Out of Stock
            </span>
          )}
        </div>

        {/* Price Row */}
        <div className="mt-auto pt-1 border-t border-neutral-100">
          <div className="flex items-baseline gap-1.5 flex-wrap mb-2">
            <span className="text-sm font-bold text-neutral-900 leading-none">
              ₹{price.toLocaleString("en-IN")}
            </span>
            {mrp && (
              <span className="text-[11px] text-neutral-400 line-through">
                MRP ₹{mrp.toLocaleString("en-IN")}
              </span>
            )}
            {discountPct > 0 && (
              <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-1 py-0.5 rounded">
                {discountPct}% OFF
              </span>
            )}
          </div>

          {/* Add to Cart Button */}
          <button
            onClick={handleAddToCart}
            disabled={adding || !isAvailable}
            className={`w-full py-1.5 px-3 text-xs font-medium rounded shadow-sm transition-all duration-150 flex items-center justify-center gap-1 ${
              added
                ? "bg-emerald-600 text-white font-semibold"
                : !isAvailable
                ? "bg-neutral-100 text-neutral-400 border border-neutral-200 cursor-not-allowed"
                : "bg-[#FC8019] hover:bg-[#e26f10] active:bg-[#c9620d] text-white font-semibold"
            }`}
          >
            {added ? (
              <>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Added to Cart
              </>
            ) : adding ? (
              "Adding..."
            ) : !isAvailable ? (
              "Out of Stock"
            ) : (
              "Add to Cart"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
