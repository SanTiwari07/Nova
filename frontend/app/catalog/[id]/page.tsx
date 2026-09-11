"use client";

import { useState, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';

export default function ProductDetail({ params }: { params: { id: string } }) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [imgSrc, setImgSrc] = useState('');
  const [addingToCart, setAddingToCart] = useState<string | null>(null);

  useEffect(() => {
    fetch(`/api/commerce/compare/${params.id}`)
      .then(res => res.json())
      .then(resData => {
        if (!resData.error) {
          setData(resData);
          setImgSrc(resData.product.image);
        }
      })
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [params.id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-50">
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mb-4"></div>
          <p className="text-neutral-500 font-medium">Analyzing purchase options...</p>
        </div>
      </div>
    );
  }

  if (!data || !data.product) {
    return <div className="min-h-screen flex items-center justify-center bg-neutral-50 text-neutral-500">Product not found</div>;
  }

  const { product, context, offers, recommendation } = data;

  const handleChoose = async (retailerId: string) => {
    setAddingToCart(retailerId);
    try {
      await fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: product.id })
      });
      // In a real app we'd add the specific offer to cart, but mock uses product_id
      window.location.href = '/cart';
    } catch (e) {
      console.error(e);
      setAddingToCart(null);
    }
  };

  const renderOffer = (offer: any, isRecommended: boolean = false) => {
    return (
      <div key={offer.retailerId} className={`p-6 rounded-2xl border ${isRecommended ? 'border-neutral-900 bg-white shadow-md relative' : 'border-neutral-200 bg-white'}`}>
        {isRecommended && (
          <div className="absolute -top-3 left-6 bg-neutral-900 text-white text-[10px] font-bold px-3 py-1 rounded-full tracking-widest uppercase">
            ✨ BEST MATCH
          </div>
        )}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-lg bg-neutral-50 border border-neutral-100 flex flex-shrink-0 items-center justify-center overflow-hidden p-1">
               {/* Just a placeholder block for logo, could use favicon api again if needed */}
               <img src={`https://www.google.com/s2/favicons?domain=${offer.retailerId === 'swiggy' ? 'swiggy.com' : offer.retailerId === 'zomato' ? 'zomato.com' : offer.retailerId === 'zepto' ? 'zeptonow.com' : offer.retailerId === 'blinkit' ? 'blinkit.com' : offer.retailerId === 'bigbasket' ? 'bigbasket.com' : 'flipkart.com'}&sz=64`} alt={offer.retailerName} className="w-full h-full object-contain" onError={(e) => e.currentTarget.style.display = 'none'} />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <h3 className="font-bold text-lg text-neutral-900">{offer.retailerName}</h3>
                <span className="text-[10px] bg-neutral-100 text-neutral-500 px-2 py-0.5 rounded font-medium">{offer.integrationType}</span>
              </div>
              <div className="flex items-center gap-2 text-sm text-neutral-500">
                <span className={`font-medium ${offer.availability === 'IN_STOCK' ? 'text-green-600' : 'text-red-500'}`}>
                  {offer.availability === 'IN_STOCK' ? 'In Stock' : 'Unavailable'}
                </span>
                {offer.availability === 'IN_STOCK' && (
                  <>
                    <span>•</span>
                    <span>{offer.deliveryEstimate}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-col md:items-end gap-1">
            <div className="flex items-center gap-4">
              <div className="flex flex-col md:items-end text-[11px] text-neutral-500 font-medium">
                <span>Product: ₹{offer.productPrice}</span>
                <span>Fees: +₹{offer.deliveryFee + offer.serviceFee}</span>
                {offer.discount > 0 && <span className="text-green-600">Discount: -₹{offer.discount}</span>}
              </div>
              <div className="text-right">
                <div className="text-2xl font-black text-neutral-900 leading-none">₹{offer.effectiveTotal}</div>
                <div className="text-[10px] text-neutral-500 font-bold tracking-wide uppercase mt-1">Effective total</div>
                
                {/* Unit price calculation attempt */}
                {(() => {
                  const match = offer.packSize.match(/([\d.]+)\s*(kg|L|ml|g|unit|pack)/i);
                  if (match && parseFloat(match[1]) > 0) {
                    const val = parseFloat(match[1]);
                    const unit = match[2].toLowerCase();
                    const perUnit = (offer.effectiveTotal / val).toFixed(2);
                    return <div className="text-[11px] text-neutral-400 font-medium mt-1">₹{perUnit}/{unit}</div>;
                  }
                  return null;
                })()}
              </div>
            </div>
          </div>
        </div>

        {isRecommended && recommendation && (
          <div className="mt-6 bg-neutral-50 rounded-xl p-4 border border-neutral-100">
            <h4 className="text-xs font-bold text-neutral-900 uppercase tracking-wider mb-2">Why recommended</h4>
            <ul className="space-y-1">
              {recommendation.reason.map((r: string, i: number) => (
                <li key={i} className="flex items-center gap-2 text-sm text-neutral-700">
                  <svg className="w-4 h-4 text-green-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                  {r}
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-6">
          <button
            onClick={() => handleChoose(offer.retailerId)}
            disabled={offer.availability !== 'IN_STOCK' || addingToCart === offer.retailerId}
            className={`w-full py-3.5 rounded-xl font-bold text-sm transition-colors flex items-center justify-center ${
              isRecommended 
                ? 'bg-neutral-900 text-white hover:bg-neutral-800' 
                : 'bg-white border-2 border-neutral-200 text-neutral-900 hover:border-neutral-900'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {addingToCart === offer.retailerId ? (
              <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin"></div>
            ) : offer.availability === 'IN_STOCK' ? (
              `Choose ${offer.retailerName}`
            ) : 'Currently Unavailable'}
          </button>
        </div>
      </div>
    );
  };

  const recommendedOffer = offers.find((o: any) => o.retailerId === recommendation.retailerId);
  const otherOffers = offers.filter((o: any) => o.retailerId !== recommendation.retailerId);

  return (
    <div className="min-h-screen bg-neutral-50 p-6 md:p-8 pt-24 pb-24">
      <div className="max-w-5xl mx-auto">
        <Link href="/catalog" className="text-neutral-500 hover:text-neutral-900 text-sm font-medium mb-8 inline-flex items-center gap-2 transition-colors">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
          Back to Catalog
        </Link>
        
        {/* Header Section */}
        <div className="bg-white rounded-3xl p-6 md:p-8 shadow-sm border border-neutral-200 mb-8 flex flex-col md:flex-row gap-8">
          <div className="w-full md:w-1/3">
            <div className="relative w-full aspect-square bg-neutral-50 rounded-2xl overflow-hidden border border-neutral-100">
              <Image
                src={imgSrc || '/assets/fallbacks/snacks.png'}
                alt={product.name}
                fill
                className="object-contain p-4"
                sizes="(max-width: 768px) 100vw, 33vw"
                onError={() => setImgSrc('/assets/fallbacks/snacks.png')}
                priority
              />
            </div>
          </div>
          
          <div className="w-full md:w-2/3 flex flex-col justify-center">
            <span className="text-xs font-bold text-neutral-400 uppercase tracking-widest mb-2">{product.brand}</span>
            <h1 className="text-2xl md:text-3xl font-black text-neutral-900 leading-tight mb-2">{product.name}</h1>
            <div className="flex items-center gap-2 mb-8">
              <span className="text-sm font-medium text-neutral-600">{product.category}</span>
              <span className="text-neutral-300">•</span>
              <span className="text-sm font-medium text-neutral-600">{product.pack_size}</span>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 p-5 bg-neutral-50 rounded-2xl border border-neutral-100">
              <div>
                <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider mb-1">Household Need</div>
                <div className="text-sm font-semibold text-neutral-900">{context.householdRequirement}</div>
              </div>
              <div>
                <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider mb-1">Current Inventory</div>
                <div className="text-sm font-semibold text-neutral-900">{context.estimatedInventory}</div>
              </div>
              <div>
                <div className="text-[10px] font-bold text-neutral-500 uppercase tracking-wider mb-1">Confidence</div>
                <div className="text-sm font-semibold text-neutral-900">{context.inventoryConfidence}%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Agent Decision Panel */}
        <div className="bg-blue-50 border border-blue-100 rounded-2xl p-6 mb-12 flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
           <div className="flex gap-4">
             <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 text-blue-600">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
             </div>
             <div>
                <h3 className="font-bold text-blue-900 mb-1">Household Autopilot Decision Context</h3>
                <p className="text-sm text-blue-800 leading-relaxed">
                  Automatic purchase limit is <strong>₹{context.autoLimit}</strong>. 
                  {recommendedOffer && recommendedOffer.effectiveTotal > context.autoLimit ? 
                    ` The recommended option exceeds this limit, so approval will be required.` : 
                    ` The recommended option is within the limit and can be purchased autonomously.`}
                </p>
             </div>
           </div>
        </div>
        
        {/* Comparison Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-black text-neutral-900 tracking-tight uppercase">Compare Purchase Options</h2>
            <div className="text-sm font-medium text-neutral-500">{offers.length} retailers found</div>
          </div>
          
          <div className="space-y-6">
            {recommendedOffer && renderOffer(recommendedOffer, true)}
            
            {otherOffers.length > 0 && (
              <div className="pt-8">
                <h3 className="text-sm font-bold text-neutral-400 uppercase tracking-wider mb-6">Other Options</h3>
                <div className="space-y-4">
                  {otherOffers.map((offer: any) => renderOffer(offer, false))}
                </div>
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
