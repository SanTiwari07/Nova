"use client";
import Link from "next/link";
import { useState } from "react";
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
        body: JSON.stringify({ product_id: product.id }),
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

      {/* Product Image */}
      <Link href={`/catalog/${product.id}`} className="block relative w-full aspect-square mb-2 overflow-hidden bg-neutral-50/50 rounded">
        <ProductImage
          src={product.imageUrl || product.image}
          alt={product.name}
          category={product.category}
          id={product.id}
          product={product}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 25vw"
          className="group-hover:scale-105 transition-transform duration-200 object-contain p-2"
        />
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
