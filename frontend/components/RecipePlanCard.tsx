import React, { useState } from 'react';
import { ShoppingCart, Check, ShieldCheck, HelpCircle } from 'lucide-react';

export default function RecipePlanCard({ plan, onAddToCart }: { plan: any, onAddToCart: (items: any[]) => void }) {
  const [adding, setAdding] = useState(false);
  const [added, setAdded] = useState(false);
  const [shoppingItems, setShoppingItems] = useState<any[]>(plan.shopping?.items || []);

  const handleAdd = async () => {
    setAdding(true);
    await onAddToCart(shoppingItems);
    setAdding(false);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  const total = shoppingItems.reduce((acc: number, item: any) => acc + (item.price || 0) * (item.quantity || 1), 0);

  const hasUncertain = plan.pantry?.uncertain?.length > 0;
  const hasShopping = shoppingItems.length > 0;
  
  let headerText = "Shopping plan ready";
  if (!hasShopping && !hasUncertain) {
      headerText = "You're all set";
  } else if (!hasShopping && hasUncertain) {
      headerText = "A couple of things need your confirmation";
  } else if (hasShopping && hasUncertain) {
      headerText = "Shopping plan ready";
  }

  return (
    <div className="bg-white border border-neutral-200 rounded-xl overflow-hidden shadow-sm mt-4 mb-4">
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-4 border-b border-neutral-200 flex justify-between items-center">
        <div>
          <h3 className="text-lg font-bold text-neutral-900">{plan.recipe?.name || plan.intent?.target || 'Recipe Plan'}</h3>
          <p className="text-sm text-neutral-600">For {plan.intent?.servings || 1} people</p>
        </div>
        <div className="text-right">
            <span className="text-xs font-semibold bg-blue-100 text-blue-800 px-2.5 py-1 rounded-full border border-blue-200">
                {headerText}
            </span>
        </div>
      </div>
      
      <div className="p-4 border-b border-neutral-100">
          <p className="text-sm text-neutral-600 mb-3">NOVA checked your pantry and recent purchases.</p>
          
          {plan.pantry && plan.pantry.available?.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-emerald-700 flex items-center gap-1.5 mb-2">
                <Check className="w-4 h-4" /> Already in your pantry
              </h4>
              <div className="flex flex-wrap gap-2">
                {plan.pantry.available.map((item: any, i: number) => (
                  <span key={i} className="px-2.5 py-1 bg-emerald-50 text-emerald-700 text-xs rounded-full border border-emerald-100 flex items-center gap-1">
                    <Check className="w-3 h-3" /> {item.name}
                  </span>
                ))}
              </div>
            </div>
          )}

          {plan.pantry && plan.pantry.uncertain?.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-semibold text-amber-700 flex items-center gap-1.5 mb-2">
                <HelpCircle className="w-4 h-4" /> Uncertain if you have enough
              </h4>
              <div className="flex flex-wrap gap-2">
                {plan.pantry.uncertain.map((item: any, i: number) => (
                  <span key={i} className="px-2.5 py-1 bg-amber-50 text-amber-800 text-xs rounded-full border border-amber-200 flex items-center gap-1">
                    <HelpCircle className="w-3 h-3" /> {item.name}
                  </span>
                ))}
              </div>
            </div>
          )}
      </div>

      {hasShopping ? (
        <div className="p-4 bg-neutral-50/50">
          <h4 className="text-sm font-semibold text-neutral-800 mb-3">Needed for this meal</h4>
          <div className="space-y-4">
            {shoppingItems.map((item: any, i: number) => (
              <div key={i} className="bg-white p-3 rounded-lg border border-neutral-200 shadow-xs flex flex-col sm:flex-row gap-4">
                <div className="w-20 h-20 bg-white rounded border border-neutral-100 overflow-hidden flex-shrink-0 flex items-center justify-center">
                  {item.imageUrl || item.image ? (
                    <img src={item.imageUrl || item.image} alt={item.name} className="w-full h-full object-contain p-1" />
                  ) : (
                    <div className="text-neutral-300 text-xs">No img</div>
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-bold text-neutral-900 leading-snug">{item.name}</p>
                  <p className="text-xs text-neutral-500 mt-0.5">Needed: {item.required_amount}</p>
                  <div className="text-xs text-neutral-600 bg-neutral-50 p-2 rounded mt-2 border border-neutral-100">
                    <span className="font-semibold">Why?</span> {item.reason || "Your pantry does not show enough for this meal."}
                  </div>
                </div>
                <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between sm:justify-start gap-2 pt-2 sm:pt-0 border-t sm:border-t-0 border-neutral-100">
                  <p className="text-base font-bold text-neutral-900">₹{((item.price || 0) * (item.quantity || 1)).toLocaleString()}</p>
                  <div className="flex items-center gap-2 mt-1 bg-white border border-neutral-200 rounded-full px-1 py-0.5">
                    <button 
                      onClick={() => {
                        const newItems = [...shoppingItems];
                        if (newItems[i].quantity > 1) newItems[i].quantity -= 1;
                        setShoppingItems(newItems);
                      }}
                      className="w-6 h-6 rounded-full hover:bg-neutral-100 flex items-center justify-center text-neutral-600 font-bold"
                    >-</button>
                    <span className="text-xs font-semibold w-4 text-center">{item.quantity}</span>
                    <button 
                      onClick={() => {
                        const newItems = [...shoppingItems];
                        newItems[i].quantity = (newItems[i].quantity || 1) + 1;
                        setShoppingItems(newItems);
                      }}
                      className="w-6 h-6 rounded-full hover:bg-neutral-100 flex items-center justify-center text-neutral-600 font-bold"
                    >+</button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="mt-5 flex flex-col sm:flex-row items-center justify-between border-t border-neutral-200 pt-4 gap-4">
            <div className="text-center sm:text-left w-full sm:w-auto">
              <p className="text-xs text-neutral-500">Shopping total</p>
              <p className="text-xl font-bold text-neutral-900">₹{total.toLocaleString()}</p>
            </div>
            <button
              onClick={handleAdd}
              disabled={adding || added}
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-6 py-3 bg-[#FFD814] hover:bg-[#F7CA00] active:bg-[#F0B800] text-neutral-900 rounded-full text-sm font-bold shadow-sm transition-colors disabled:opacity-50 cursor-pointer"
            >
              {added ? <Check className="w-5 h-5" /> : <ShoppingCart className="w-5 h-5" />}
              {adding ? 'Adding...' : added ? 'Added to Cart' : `Add ${shoppingItems.length} items to cart · ₹${total.toLocaleString()}`}
            </button>
          </div>
        </div>
      ) : (
        <div className="p-4 text-center">
          <p className="text-sm font-medium text-neutral-700">You already have everything needed for this meal.</p>
        </div>
      )}
    </div>
  );
}
