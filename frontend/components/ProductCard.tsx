"use client";
import Link from "next/link";
import { useState } from "react";
import ProductImage from "./ProductImage";

interface Product {
  id: string;
  name: string;
  brand: string;
  price: number;
  currency: string;
  pack_size: string;
  image: string;
  category?: string;
  tags?: string[];
  confidence?: number;
  typical_interval_days?: number;
  days_until_needed?: number;
  avg_price?: number;
  source?: string;
}

export default function ProductCard({ product }: { product: Product }) {
  const [addedToNova, setAddedToNova] = useState(false);

  const handleAddToNovaCart = async (e: React.MouseEvent) => {
    e.preventDefault();
    await fetch("/api/nova-cart/items", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: product.id, quantity: 1 }),
    });
    setAddedToNova(true);
    setTimeout(() => setAddedToNova(false), 2000);
  };

  const isUsual = product.tags?.includes("usual");
  const isRecommended = product.tags?.includes("recommended");
  const neededSoon = product.days_until_needed !== undefined && product.days_until_needed <= 7;
  const belowAvg = product.avg_price && product.price < product.avg_price;
  const priceDiffPct = product.avg_price
    ? Math.round(((product.price - product.avg_price) / product.avg_price) * 100)
    : null;

  return (
    <Link
      href={`/catalog/${product.id}`}
      className="group block border border-neutral-100 rounded-2xl p-4 bg-white hover:shadow-xl hover:border-neutral-200 transition-all duration-300 relative flex flex-col h-full"
    >
      {/* Badges */}
      <div className="absolute top-2 left-2 z-10 flex flex-col gap-1">
        {neededSoon && (
          <span className="px-2 py-0.5 bg-[#FF9900] text-white text-[9px] font-bold tracking-wide rounded-md">
            DUE IN {product.days_until_needed}D
          </span>
        )}
        {isUsual && !neededSoon && (
          <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-[9px] font-bold tracking-wide rounded-md">
            YOUR USUAL
          </span>
        )}
        {isRecommended && !isUsual && !neededSoon && (
          <span className="px-2 py-0.5 bg-orange-50 text-orange-700 text-[9px] font-bold tracking-wide rounded-md">
            NOVA PICK
          </span>
        )}
        {belowAvg && (
          <span className="px-2 py-0.5 bg-green-50 text-green-700 text-[9px] font-bold tracking-wide rounded-md">
            {Math.abs(priceDiffPct || 0)}% BELOW AVG
          </span>
        )}
      </div>

      {/* Image */}
      <div className="relative w-full aspect-square mb-3 rounded-xl overflow-hidden bg-neutral-50">
        <ProductImage
          src={product.image}
          alt={product.name}
          category={product.category}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />
      </div>

      <div className="flex flex-col flex-grow">
        <span className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-0.5">
          {product.brand}
        </span>
        <h3 className="text-sm font-medium text-neutral-800 line-clamp-2 leading-tight mb-1 group-hover:text-neutral-900">
          {product.name}
        </h3>
        <span className="text-xs text-neutral-400 mb-2">{product.pack_size}</span>

        {/* NOVA intelligence insight */}
        {product.typical_interval_days && (
          <p className="text-[10px] text-neutral-400 mb-2 leading-relaxed">
            {neededSoon
              ? `Usually needed in ${product.typical_interval_days}d · Due in ${product.days_until_needed}d`
              : `Usually bought every ${product.typical_interval_days} days`}
            {product.confidence
              ? ` · ${Math.round(product.confidence * 100)}% confident`
              : ""}
          </p>
        )}

        <div className="mt-auto pt-3 border-t border-neutral-100">
          <div className="flex items-center justify-between mb-2">
            <span className="text-lg font-black text-neutral-900">₹{product.price}</span>
            <span className="text-[10px] font-semibold text-[#FF9900]">Prime ✓</span>
          </div>
          <button
            onClick={handleAddToNovaCart}
            className={`w-full py-2 rounded-xl text-xs font-bold transition-all ${
              addedToNova
                ? "bg-green-100 text-green-700"
                : "bg-[#FF9900]/10 text-[#FF9900] hover:bg-[#FF9900]/20"
            }`}
          >
            {addedToNova ? "✓ Added to NOVA Cart" : "+ NOVA Cart"}
          </button>
        </div>
      </div>
    </Link>
  );
}
