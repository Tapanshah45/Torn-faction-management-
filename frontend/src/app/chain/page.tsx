'use client';
import { useLiveUpdates } from '@/hooks/useLiveUpdates';
import Sidebar from '@/components/layout/Sidebar';
import { Link2, TriangleAlert, Clock3, UserX } from 'lucide-react';

export default function ChainTracker() {
  const { chainData, chainBreakEvent, isConnected } = useLiveUpdates();
  const currentChain = String(chainData?.current ?? chainData?.chain ?? chainData?.count ?? 0);
  const timerValue = String(chainData?.time_remaining ?? chainData?.timer ?? chainData?.timeLeft ?? 'N/A');

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

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2 bg-gray-800 p-8 rounded-xl border border-gray-700">
            {chainData ? (
              <div className="space-y-4">
                <div className="flex items-end justify-between gap-4 flex-wrap">
                  <div>
                    <p className="text-gray-400 uppercase tracking-widest text-sm">Current Chain</p>
                    <p className="text-6xl font-black text-purple-400">{currentChain}</p>
                  </div>
                  <div className="bg-gray-900/60 px-4 py-3 rounded-lg border border-gray-700 flex items-center gap-3">
                    <Clock3 className="text-yellow-400" />
                    <div>
                      <p className="text-xs text-gray-400 uppercase tracking-widest">Time Remaining</p>
                      <p className="font-semibold">{String(timerValue)}</p>
                    </div>
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-4">
                    <p className="text-xs uppercase tracking-widest text-gray-400 mb-2">Last Hitter</p>
                    <p className="font-semibold">{String(chainData?.last_hitter_name ?? chainData?.last_hit_member ?? 'Unknown')}</p>
                  </div>
                  <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-4">
                    <p className="text-xs uppercase tracking-widest text-gray-400 mb-2">Expected Next Hit By</p>
                    <p className="font-semibold">{String(chainData?.expected_next_hit_by ?? chainData?.next_hit_by ?? 'N/A')}</p>
                  </div>
                  <div className={`border rounded-lg p-4 ${chainBreakEvent?.chain_broken ? 'bg-red-950/40 border-red-700' : 'bg-gray-900/60 border-gray-700'}`}>
                    <p className="text-xs uppercase tracking-widest text-gray-400 mb-2">Status</p>
                    <p className="font-semibold">{chainBreakEvent?.chain_broken ? 'Broken' : 'Monitoring'}</p>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-gray-500">Waiting for chain data...</p>
            )}
          </div>

          <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 space-y-4">
            <div className="flex items-center gap-3">
              <TriangleAlert className="text-red-400" />
              <h2 className="text-xl font-semibold">Chain Alerts</h2>
            </div>
            {chainBreakEvent ? (
              <div className="space-y-3 text-sm">
                <div className="p-3 rounded-lg border border-red-700 bg-red-950/40">
                  <p className="text-red-300 font-semibold">{chainBreakEvent.reason}</p>
                  <p className="text-gray-300 mt-1">Chain ID: {chainBreakEvent.chain_id}</p>
                </div>
                <div className="p-3 rounded-lg border border-gray-700 bg-gray-900/50">
                  <div className="flex items-center gap-2 text-gray-300">
                    <UserX size={16} className="text-orange-400" />
                    <span>Suspected Breaker</span>
                  </div>
                  <p className="mt-2 font-medium">{chainBreakEvent.last_hitter_name || 'Unknown'}</p>
                  <p className="text-gray-400 mt-1">Time remaining: {chainBreakEvent.time_remaining ?? 'N/A'} sec</p>
                </div>
              </div>
            ) : (
              <p className="text-gray-500 text-sm">No critical chain warnings yet.</p>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
