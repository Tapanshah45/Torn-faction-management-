'use client';
import { useLiveUpdates } from '@/hooks/useLiveUpdates';
import Sidebar from '@/components/layout/Sidebar';
import { Link2 } from 'lucide-react';

export default function ChainTracker() {
  const { chainData, isConnected } = useLiveUpdates();

  return (
    <div className="flex min-h-screen bg-gray-900 text-white">
      <Sidebar />
      <main className="flex-1 p-8">
        <div className="flex items-center justify-between mb-8 border-b border-gray-700 pb-4">
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Link2 className="text-purple-500" />
            Live Chain Tracker
          </h1>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-gray-400">{isConnected ? 'Live' : 'Disconnected'}</span>
          </div>
        </div>

        <div className="bg-gray-800 p-8 rounded-xl border border-gray-700 text-center">
          {chainData ? (
            <div>
              <p className="text-6xl font-black text-purple-400 mb-4">{chainData.current || 0}</p>
              <p className="text-gray-400 text-xl uppercase tracking-widest">Current Chain</p>
            </div>
          ) : (
            <p className="text-gray-500">Waiting for chain data...</p>
          )}
        </div>
      </main>
    </div>
  );
}
