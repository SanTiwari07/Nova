import Image from 'next/image';
import { useState, useEffect } from 'react';

interface ProductImageProps {
  src?: string;
  alt: string;
  category?: string;
  className?: string;
  sizes?: string;
  fill?: boolean;
  width?: number;
  height?: number;
}

export default function ProductImage({ 
  src, 
  alt, 
  category = 'generic', 
  className = '', 
  sizes,
  fill,
  width,
  height
}: ProductImageProps) {
  const fallbackCategory = category ? category.toLowerCase().replace(/[^a-z0-9]/g, '') : 'generic';
  
  const getFallbackUrl = () => {
    const mapping: Record<string, string> = {
      'rice': '/assets/fallbacks/rice.webp',
      'milk': '/assets/fallbacks/milk.webp',
      'oil': '/assets/fallbacks/oil.webp',
      'noodles': '/assets/fallbacks/noodles.webp',
      'tea': '/assets/fallbacks/tea.png',
      'snacks': '/assets/fallbacks/snacks.png',
      'atta': '/assets/fallbacks/atta.png',
      'spices': '/assets/fallbacks/spices.png',
      'detergent': '/assets/fallbacks/detergent.png',
      'shampoo': '/assets/fallbacks/haircare.png',
      'chocolates': '/assets/fallbacks/chocolates.png',
      'drinks': '/assets/fallbacks/drinks.png',
      'bath': '/assets/fallbacks/bath.png',
      'haircare': '/assets/fallbacks/haircare.png',
      'skincare': '/assets/fallbacks/skincare.png',
      'biscuits': '/assets/fallbacks/biscuits.png',
      'coffee': '/assets/fallbacks/coffee.png',
      'dal': '/assets/fallbacks/dal.png',
      'deodorant': '/assets/fallbacks/deodorant.png',
      'dishwash': '/assets/fallbacks/dishwash.png',
      'breakfast': '/assets/fallbacks/breakfast.png'
    };
    
    for (const [key, url] of Object.entries(mapping)) {
      if (fallbackCategory.includes(key)) {
        return url;
      }
    }
    
    return `/assets/fallbacks/${fallbackCategory}.png`;
  };

  const [imgSrc, setImgSrc] = useState<string>(src || getFallbackUrl());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setImgSrc(src || getFallbackUrl());
    setLoading(true);
  }, [src, category]);

  return (
    <div className={`relative flex items-center justify-center bg-neutral-50 overflow-hidden ${className}`}>
      {loading && (
        <div className="absolute inset-0 bg-neutral-100 animate-pulse flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-neutral-300 border-t-neutral-400 rounded-full animate-spin"></div>
        </div>
      )}
      <Image
        src={imgSrc}
        alt={alt}
        fill={fill}
        width={width}
        height={height}
        className={`object-contain transition-opacity duration-300 ${loading ? 'opacity-0' : 'opacity-100'}`}
        sizes={sizes}
        onLoadingComplete={() => setLoading(false)}
        onError={() => {
          setLoading(false);
          if (imgSrc !== getFallbackUrl()) {
            setImgSrc(getFallbackUrl());
          } else if (imgSrc !== '/assets/fallbacks/snacks.png') {
            setImgSrc('/assets/fallbacks/snacks.png');
          }
        }}
      />
    </div>
  );
}
