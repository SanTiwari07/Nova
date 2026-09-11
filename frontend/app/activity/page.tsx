"use client";

import { useState, useEffect } from 'react';

interface AuditLog {
  id: string;
  product: string;
  decision: string;
  reasons: string[];
  timestamp: string;
}

export default function ActivityPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);

  useEffect(() => {
    fetch('/api/audit/activity')
      .then(res => res.json())
      .then(data => setLogs(data));
  }, []);

  const formatTime = (ts: string) => {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getBadgeClass = (decision: string) => {
    switch (decision) {
      case 'AUTO': return 'bg-green-100 text-green-800 border border-green-200';
      case 'DO_NOTHING': return 'bg-neutral-100 text-neutral-600 border border-neutral-200';
      case 'ASK': return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
      case 'BLOCKED': return 'bg-red-100 text-red-800 border border-red-200';
      default: return 'bg-neutral-100 text-neutral-800';
    }
  };
  
  const getHumanDecision = (decision: string) => {
    switch (decision) {
      case 'AUTO': return 'Taken care of';
      case 'DO_NOTHING': return 'No action needed';
      case 'ASK': return 'Needs your input';
      case 'BLOCKED': return "Can't do this under your rules";
      default: return decision;
    }
  };

  return (
    <div className="min-h-screen bg-neutral-50 p-8 pt-24 font-sans pb-24">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold text-neutral-900 mb-8">Recently Taken Care Of</h1>
        
        <div className="space-y-4">
          {logs.map(log => (
            <div key={log.id} className="bg-white p-6 rounded-2xl shadow-sm border border-neutral-200">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="font-bold text-lg">{log.product}</h3>
                  <div className="flex items-center gap-3 mt-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getBadgeClass(log.decision)}`}>
                      {getHumanDecision(log.decision)}
                    </span>
                    <span className="text-sm text-neutral-400">{formatTime(log.timestamp)}</span>
                  </div>
                </div>
              </div>
              <div className="bg-neutral-50 rounded-xl p-4 mt-4 text-sm text-neutral-600 space-y-1">
                <p className="font-medium text-neutral-800 mb-2">Why?</p>
                <ul className="list-disc list-inside pl-4 space-y-1">
                  {log.reasons.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
          
          {logs.length === 0 && (
            <div className="text-center text-neutral-500 py-12">
              No recent activity.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
