import ProductCard from './ProductCard';
import { useRef } from 'react';

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

interface ProductShelfProps {
  title: string;
  products: Product[];
  viewAllLink?: string;
}

export default function ProductShelf({ title, products, viewAllLink }: ProductShelfProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  const scroll = (direction: 'left' | 'right') => {
    if (scrollRef.current) {
      const { scrollLeft, clientWidth } = scrollRef.current;
      const scrollTo = direction === 'left' ? scrollLeft - clientWidth + 40 : scrollLeft + clientWidth - 40;
      scrollRef.current.scrollTo({ left: scrollTo, behavior: 'smooth' });
    }
  };

  if (!products || products.length === 0) return null;

  return (
    <div className="mb-12">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl md:text-2xl font-bold text-neutral-900 tracking-tight uppercase">{title}</h2>
        <div className="flex items-center gap-4">
          {viewAllLink && (
            <a href={viewAllLink} className="hidden md:block text-sm font-semibold text-neutral-500 hover:text-neutral-900 transition-colors uppercase tracking-wider">
              View All →
            </a>
          )}
          <div className="hidden md:flex items-center gap-2">
            <button onClick={() => scroll('left')} className="w-8 h-8 rounded-full border border-neutral-200 flex items-center justify-center text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
            </button>
            <button onClick={() => scroll('right')} className="w-8 h-8 rounded-full border border-neutral-200 flex items-center justify-center text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 transition-colors">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>
        </div>
      </div>
      
      <div className="relative -mx-6 px-6 md:mx-0 md:px-0">
        <div 
          ref={scrollRef}
          className="flex overflow-x-auto gap-4 md:gap-6 pb-6 pt-2 snap-x snap-mandatory hide-scrollbar"
          style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
        >
          {products.map(product => (
            <div key={product.id} className="min-w-[220px] max-w-[220px] md:min-w-[240px] md:max-w-[240px] flex-shrink-0 snap-start">
              <ProductCard product={product} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
