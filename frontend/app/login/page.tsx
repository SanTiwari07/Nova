"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    // Call mock auth endpoint
    await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email || 'demo@nova.local' })
    });
    
    router.push('/onboarding/services');
  };

  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col justify-center items-center font-sans p-8">
      <div className="w-full max-w-md bg-white p-12 rounded-2xl shadow-sm border border-neutral-100 text-center">
        <div className="flex justify-center mb-4">
          <img
            src="/logo.png"
            alt="NOVA"
            className="h-10 sm:h-12 w-auto object-contain"
          />
        </div>
        <p className="text-neutral-500 mb-8">Your everyday life, a little lighter.</p>
        
        <h2 className="text-xl font-medium mb-6">Welcome back</h2>
        
        <form onSubmit={handleLogin} className="flex flex-col gap-4">
          <button type="button" className="w-full py-3 border border-neutral-300 rounded-lg font-medium hover:bg-neutral-50">
            Continue with Google
          </button>
          
          <div className="relative flex items-center py-2">
            <div className="flex-grow border-t border-neutral-200"></div>
            <span className="flex-shrink-0 mx-4 text-neutral-400 text-sm">or</span>
            <div className="flex-grow border-t border-neutral-200"></div>
          </div>
          
          <input 
            type="email" 
            placeholder="Email" 
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full p-3 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
          />
          <input 
            type="password" 
            placeholder="Password" 
            className="w-full p-3 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-neutral-900"
          />
          
          <button 
            type="submit" 
            disabled={loading}
            className="w-full py-4 mt-4 bg-neutral-900 text-white rounded-xl font-medium hover:bg-neutral-800 disabled:opacity-50"
          >
            {loading ? 'Logging in...' : 'Login (Demo)'}
          </button>
        </form>
        
        <p className="mt-6 text-sm text-neutral-500">
          Note: Authentication is MOCK. Click login to continue.
        </p>
      </div>
    </div>
  );
}
