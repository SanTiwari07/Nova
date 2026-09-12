"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Check } from 'lucide-react';

export default function ConnectServicesPage() {
  const router = useRouter();
  const [connecting, setConnecting] = useState<string | null>(null);
  const [connected, setConnected] = useState<string[]>([]);
  
  const providers = [
    { name: "Blinkit", domain: "blinkit.com" },
    { name: "Zepto", domain: "zeptonow.com" },
    { name: "Swiggy", domain: "swiggy.com" },
    { name: "Zomato", domain: "zomato.com" },
    { name: "BigBasket", domain: "bigbasket.com" },
    { name: "Flipkart", domain: "flipkart.com" }
  ];

  const handleConnect = async (provider: string) => {
    setConnecting(provider);
    
    // Simulate connection delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    await fetch('/api/onboarding/services', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider })
    });
    
    setConnected(prev => [...prev, provider]);
    setConnecting(null);
  };

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans flex flex-col items-center">
      <div className="max-w-3xl w-full">
        <h1 className="text-3xl font-bold text-neutral-900 mb-2">Connect your everyday shopping</h1>
        <p className="text-neutral-500 mb-12 text-lg">NOVA can work across the services you already use.</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-12">
          {providers.map(provider => (
            <div key={provider.name} className="bg-white p-6 rounded-xl border border-neutral-200 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-lg bg-neutral-50 border border-neutral-100 flex items-center justify-center overflow-hidden flex-shrink-0">
                  <img 
                    src={`https://www.google.com/s2/favicons?domain=${provider.domain}&sz=128`} 
                    alt={`${provider.name} logo`} 
                    className="w-8 h-8 object-contain"
                  />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{provider.name}</h3>
                  <p className="text-xs text-neutral-400 mt-1">Demo Integration</p>
                </div>
              </div>
              
              {connected.includes(provider.name) ? (
                <span className="flex items-center gap-1 text-green-600 font-medium px-4 py-2 bg-green-50 rounded-lg">
                  <Check className="w-4 h-4" /> Connected
                </span>
              ) : connecting === provider.name ? (
                <span className="text-neutral-500 font-medium px-4 py-2 bg-neutral-100 rounded-lg">Connecting...</span>
              ) : (
                <button 
                  onClick={() => handleConnect(provider.name)}
                  className="px-4 py-2 bg-neutral-900 text-white rounded-lg font-medium hover:bg-neutral-800"
                >
                  Connect
                </button>
              )}
            </div>
          ))}
        </div>
        
        <div className="flex justify-end">
          <button 
            onClick={() => router.push('/onboarding/autonomy')}
            disabled={connected.length === 0}
            className="px-8 py-4 bg-neutral-900 text-white rounded-xl font-medium hover:bg-neutral-800 disabled:opacity-50"
          >
            Continue
          </button>
        </div>
        
        {connected.length === 0 && (
          <p className="text-right text-sm text-neutral-500 mt-4">Please connect at least one mock service.</p>
        )}
      </div>
    </div>
  );
}
