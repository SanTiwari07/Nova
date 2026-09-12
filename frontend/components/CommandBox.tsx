import { useState } from 'react';
import { Sparkles } from 'lucide-react';

export default function CommandBox() {
  const [command, setCommand] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading || !command) return;
    setLoading(true);
    setResponse('Autopilot is thinking...');
    
    try {
      const res = await fetch('/api/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: command })
      });
      const data = await res.json();
      setResponse(data.response);
    } catch (err) {
      setResponse('Error connecting to Autopilot backend.');
    } finally {
      setCommand('');
      setLoading(false);
    }
  };

  return (
    <div className="w-full mb-16">
      <form onSubmit={handleSubmit} className="relative group">
        <div className="absolute inset-y-0 left-0 pl-6 flex items-center pointer-events-none">
          <Sparkles className="text-orange-500 w-5 h-5" />
        </div>
        <input 
          type="text" 
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Tell Autopilot what you're trying to do..."
          className="w-full pl-14 pr-40 py-5 rounded-2xl bg-white border border-neutral-200 shadow-sm text-lg focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-transparent transition-all placeholder:text-neutral-400"
        />
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
          <button 
            type="submit" 
            disabled={loading || !command}
            className="px-6 py-3 bg-neutral-900 text-white rounded-xl hover:bg-neutral-800 disabled:opacity-50 font-semibold transition-colors"
          >
            {loading ? 'Asking...' : 'Ask Autopilot'}
          </button>
        </div>
      </form>
      
      {response && (
        <div className="mt-4 bg-orange-50 border border-orange-100 rounded-2xl p-6 shadow-sm relative overflow-hidden">
          <div className="absolute top-0 left-0 w-1 h-full bg-orange-400"></div>
          <div className="flex items-start gap-4">
            <div className="mt-1 text-orange-500">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-xs text-orange-700 font-bold uppercase tracking-wider mb-2">Autopilot Response</h3>
              <p className="text-base text-neutral-800 leading-relaxed whitespace-pre-wrap">{response}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
