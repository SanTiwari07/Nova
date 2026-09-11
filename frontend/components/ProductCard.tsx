import Link from 'next/link';
import { useState } from 'react';
import ProductImage from './ProductImage';

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
}

export default function ProductCard({ product }: { product: Product }) {
  const [adding, setAdding] = useState(false);

  const handleAdd = async (e: React.MouseEvent) => {
    e.preventDefault();
    if (adding) return;
    setAdding(true);
    try {
      await fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: product.id })
      });
    } finally {
      setAdding(false);
    }
  };

  const isUsual = product.tags?.includes('usual');
  const isRecommended = product.tags?.includes('recommended');
  
  return (
    <Link href={`/catalog/${product.id}`} className="group block border border-neutral-100 rounded-2xl p-4 bg-white hover:shadow-xl hover:border-neutral-200 transition-all duration-300 relative flex flex-col h-full">
      
      {/* AI Badges */}
      <div className="absolute top-2 left-2 z-10 flex flex-col gap-1">
        {isUsual && (
          <span className="px-2 py-1 bg-blue-50 text-blue-700 text-[10px] font-bold tracking-wide rounded-md">
            YOUR USUAL
          </span>
        )}
        {isRecommended && (
          <span className="px-2 py-1 bg-orange-50 text-orange-700 text-[10px] font-bold tracking-wide rounded-md">
            AI PICK
          </span>
        )}
      </div>

      <div className="relative w-full aspect-square mb-4 rounded-xl overflow-hidden">
        <ProductImage
          src={product.image}
          alt={product.name}
          category={product.category}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />
      </div>
      
      <div className="flex flex-col flex-grow">
        <span className="text-[10px] font-bold text-neutral-400 uppercase tracking-wider mb-1">{product.brand}</span>
        <h3 className="text-sm font-medium text-neutral-800 line-clamp-2 leading-tight mb-1 group-hover:text-neutral-900">{product.name}</h3>
        <span className="text-xs text-neutral-500 mb-4">{product.pack_size}</span>
        
        <div className="mt-auto pt-4 border-t border-neutral-100">
          <div className="flex flex-col">
            <span className="text-[11px] text-neutral-500 font-medium mb-1">From ₹{Math.floor(product.price * 0.9)} • 6 retailers</span>
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold text-neutral-900">₹{product.price}</span>
              <span className="text-sm font-bold text-neutral-900 flex items-center gap-1 group-hover:text-blue-600 transition-colors">
                Compare <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
              </span>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
}
