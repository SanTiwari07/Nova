"use client";

import { useState, useEffect, useCallback } from 'react';
import ProductShelf from '@/components/ProductShelf';
import CommandBox from '@/components/CommandBox';
import AutopilotHero from '@/components/AutopilotHero';
import HouseholdStatus from '@/components/HouseholdStatus';
import DecisionCard from '@/components/DecisionCard';
import CategoryCard from '@/components/CategoryCard';

export default function StorePage() {
  const [loading, setLoading] = useState(true);
  const [budget, setBudget] = useState({ remaining: 0 });
  const [pantry, setPantry] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [decisions, setDecisions] = useState<any[]>([]);
  
  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [budgetRes, pantryRes, productsRes, catsRes] = await Promise.all([
          fetch('/api/budget').then(r => r.json()),
          fetch('/api/pantry').then(r => r.json()),
          fetch('/api/products?limit=100').then(r => r.json()),
          fetch('/api/products/categories').then(r => r.json())
        ]);
        
        setBudget(budgetRes);
        setPantry(pantryRes);
        setProducts(productsRes);
        setCategories(catsRes);
        
        const generatedDecisions = [];
        const milk = pantryRes.find((i: any) => i.name.toLowerCase().includes('milk'));
        if (milk && milk.status === 'LOW') {
          generatedDecisions.push({
            id: 'd1',
            type: 'BUY',
            category: 'Milk',
            confidence: 92,
            inventoryState: `${milk.quantity}${milk.unit}`,
            depletionEstimate: 'Tomorrow',
            product: productsRes.find((p: any) => p.name.includes('Milk')) || { name: 'Amul Taaza Milk 1L', price: 68 },
            reasoning: [
              'Estimated inventory is low.',
              'Expected depletion is tomorrow.',
              'Inventory confidence is 92%.',
              'The selected product matches preferred brand.',
              'Cost is within your ₹500 automatic limit.'
            ]
          });
        }
        
        const oil = pantryRes.find((i: any) => i.name.toLowerCase().includes('oil'));
        if (oil && (oil.status === 'HEALTHY' || true)) {
          generatedDecisions.push({
            id: 'd2',
            type: 'DO_NOT_BUY',
            category: 'Cooking Oil',
            confidence: 88,
            inventoryState: oil ? `${oil.quantity}${oil.unit}` : '2.4L',
            depletionEstimate: '~3 months',
            reasoning: [
              'Estimated inventory is healthy.',
              'Expected remaining duration is approximately 3 months.',
              'No immediate purchase required.'
            ]
          });
        }
        
        setDecisions(generatedDecisions);
      } catch (err) {
        console.error("Failed to load store data", err);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-neutral-50 p-8 pt-24 pb-24 flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-neutral-200 border-t-neutral-900 rounded-full animate-spin mb-4"></div>
          <p className="text-neutral-500 font-medium">Loading your household...</p>
        </div>
      </div>
    );
  }

  // Deduplicate products by category for Autopilot Recommends so it's not all Rice
  const recommendationsMap = new Map();
  products.forEach(p => {
    if (!recommendationsMap.has(p.category)) {
      recommendationsMap.set(p.category, { ...p, tags: ['recommended'] });
    }
  });
  const autopilotRecommends = Array.from(recommendationsMap.values()).slice(0, 10);
  
  const usuals = products.filter(p => p.name.includes('Tea') || p.name.includes('Coffee') || p.name.includes('Oil')).slice(0, 10).map(p => ({...p, tags: ['usual']}));
  
  const cookingEssentials = products.filter(p => p.category === 'Oil' || p.category === 'Spices').slice(0, 10);
  const riceAndGrains = products.filter(p => p.category === 'Rice' || p.category === 'Atta').slice(0, 10);
  const dalAndPulses = products.filter(p => p.category === 'Dal' || p.name.toLowerCase().includes('dal')).slice(0, 10);
  const breakfast = products.filter(p => p.category === 'Breakfast' || p.name.toLowerCase().includes('oats')).slice(0, 10);
  const snacksAndBeverages = products.filter(p => ['Snacks', 'Beverages', 'Tea', 'Coffee', 'Chocolates'].includes(p.category)).slice(0, 10);
  const householdEssentials = products.filter(p => ['Detergent', 'Dishwash', 'Cleaning', 'Laundry'].includes(p.category)).slice(0, 10);
  const personalCare = products.filter(p => ['Deodorant', 'Bath', 'Hair Care', 'Skin Care'].includes(p.category)).slice(0, 10);
  const discoverNewFinds = products.slice(10, 25);
  
  // Deals
  const deals = products.slice(0, 8).map(p => ({ ...p, tags: ['deal'] }));

  // Shop by Category Configuration
  const groceryCats = [
    { name: 'Atta', key: 'atta' }, { name: 'Rice', key: 'rice' }, { name: 'Dal', key: 'dal' },
    { name: 'Oil', key: 'oil' }, { name: 'Breakfast', key: 'breakfast' }, { name: 'Snacks', key: 'snacks' },
    { name: 'Tea', key: 'tea' }, { name: 'Coffee', key: 'coffee' }, { name: 'Biscuits', key: 'biscuits' },
    { name: 'Noodles', key: 'noodles' }, { name: 'Drinks', key: 'drinks' }, { name: 'Chocolates', key: 'chocolates' }
  ];
  
  const beautyCats = [
    { name: 'Bath & Body', key: 'bath' }, { name: 'Hair Care', key: 'haircare' },
    { name: 'Skin Care', key: 'skincare' }, { name: 'Deodorant', key: 'deodorant' }
  ];
  
  const householdCats = [
    { name: 'Detergent', key: 'detergent' }, { name: 'Dishwash', key: 'dishwash' }
  ];

  const renderCategoryGroup = (title: string, catList: any[]) => (
    <div className="mb-10">
      <h3 className="text-lg font-bold text-neutral-700 mb-6">{title}</h3>
      <div className="flex flex-wrap gap-4 md:gap-6 pb-4">
        {catList.map((cat, i) => {
          const ext = ['milk', 'rice', 'noodles', 'oil'].includes(cat.key) ? 'webp' : 'png';
          return (
            <div key={i} className="flex-shrink-0">
              <CategoryCard 
                name={cat.name} 
                image={`/assets/fallbacks/${cat.key}.${ext}`} 
                href={`/catalog?category=${cat.name}`} 
              />
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-neutral-50 pb-24">
      {/* Header handled by Layout usually, but we ensure content is contained */}
      <div className="max-w-[1400px] mx-auto w-full">
        
        {/* HERO SECTION */}
        <div className="px-4 md:px-8 pt-6">
          <AutopilotHero 
            trackedItems={pantry.length || 18} 
            decisionsCount={decisions.filter(d => d.type === 'ASK_USER' || d.type === 'BUY').length || 1} 
            budgetRemaining={budget.remaining || 1200} 
          />
        </div>

        <div className="px-4 md:px-8 mt-4">
          <HouseholdStatus 
            trackedItems={pantry.length || 18} 
            healthPercent={82} 
            budgetRemaining={budget.remaining || 1200} 
            autonomyOn={true} 
            decisionsCount={decisions.filter(d => d.type === 'ASK_USER' || d.type === 'BUY').length} 
          />
        </div>

        {/* DECISIONS */}
        {decisions.length > 0 && (
          <div id="decisions" className="px-4 md:px-8 mt-12 mb-12">
            <h2 className="text-xl md:text-2xl font-black text-neutral-900 tracking-tight mb-6">Autopilot Decisions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {decisions.map(decision => (
                <DecisionCard key={decision.id} decision={decision} />
              ))}
            </div>
          </div>
        )}

        {/* COMMAND BAR */}
        <div className="px-4 md:px-8 mb-12">
          <CommandBox />
        </div>

        {/* SHOP BY CATEGORY */}
        <div className="px-4 md:px-8 py-12 bg-white mb-12 border-y border-neutral-100">
          <h2 className="text-2xl md:text-3xl font-black text-neutral-900 tracking-tight mb-8">Shop by Category</h2>
          {renderCategoryGroup("GROCERIES & FOOD", groceryCats)}
          {renderCategoryGroup("BEAUTY & PERSONAL CARE", beautyCats)}
          {renderCategoryGroup("HOUSEHOLD ESSENTIALS", householdCats)}
        </div>

        {/* COMMERCE SHELVES */}
        <div className="px-4 md:px-8 mb-8 space-y-12">
          <ProductShelf title="Autopilot Recommends" products={autopilotRecommends} />
        </div>

        <div className="bg-orange-50 px-4 md:px-8 py-12 mb-12 border-y border-orange-100">
          <ProductShelf title="Deals For Your Household" products={deals} />
        </div>

        <div className="px-4 md:px-8 mb-12 space-y-16">
          {cookingEssentials.length > 0 && <ProductShelf title="Cooking Essentials" products={cookingEssentials} viewAllLink="/catalog" />}
          {riceAndGrains.length > 0 && <ProductShelf title="Rice & Grains" products={riceAndGrains} viewAllLink="/catalog" />}
          {dalAndPulses.length > 0 && <ProductShelf title="Dal & Pulses" products={dalAndPulses} viewAllLink="/catalog" />}
          {breakfast.length > 0 && <ProductShelf title="Breakfast" products={breakfast} viewAllLink="/catalog" />}
          {snacksAndBeverages.length > 0 && <ProductShelf title="Snacks & Beverages" products={snacksAndBeverages} viewAllLink="/catalog" />}
        </div>

        <div className="bg-blue-50 px-4 md:px-8 py-12 mb-12 border-y border-blue-100">
          {householdEssentials.length > 0 && <ProductShelf title="Household Essentials" products={householdEssentials} viewAllLink="/catalog" />}
          {personalCare.length > 0 && <ProductShelf title="Personal Care" products={personalCare} viewAllLink="/catalog" />}
        </div>

        <div className="bg-yellow-50 px-4 md:px-8 py-12 border-t border-yellow-100">
          {discoverNewFinds.length > 0 && <ProductShelf title="Discover New Finds" products={discoverNewFinds} viewAllLink="/catalog" />}
        </div>
        
        <div className="px-4 md:px-8 py-12 mb-12">
          <h2 className="text-xl md:text-2xl font-black text-neutral-900 tracking-tight mb-8">Shop by Need</h2>
          <div className="flex flex-wrap gap-4">
            {['Local Favourites', 'Organic', 'Health & Wellness', 'Healthy Eating', 'Pet Care', 'Quick Meals'].map(need => (
              <button key={need} className="px-6 py-3 bg-white border border-neutral-200 rounded-full font-bold text-neutral-700 hover:border-neutral-900 hover:text-neutral-900 shadow-sm transition-all">{need}</button>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
