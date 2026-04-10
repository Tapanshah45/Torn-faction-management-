'use client';

import { useEffect, useMemo, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import { safeStorage } from '@/lib/safeStorage';
import { ShieldAlert, Search, Filter, ArrowDownAZ } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Tooltip } from 'recharts';

type ReliabilityRow = {
  id: number;
  member: number;
  member_detail?: { name: string };
  activity_score: string;
  chain_score: string;
  war_score: string;
  oc_score: string;
  final_score: string;
  risk_level: 'highly_reliable' | 'stable' | 'at_risk' | 'high_kick_risk';
  updated_at: string;
};

const riskLabels = {
  highly_reliable: 'Highly Reliable',
  stable: 'Stable',
  at_risk: 'At Risk',
  high_kick_risk: 'High Kick Risk',
};

const riskStyles = {
  highly_reliable: 'bg-green-900 text-green-300 border-green-700',
  stable: 'bg-sky-900 text-sky-300 border-sky-700',
  at_risk: 'bg-amber-900 text-amber-300 border-amber-700',
  high_kick_risk: 'bg-red-900 text-red-300 border-red-700',
};

export default function ReliabilityPage() {
  const [rows, setRows] = useState<ReliabilityRow[]>([]);
  const [search, setSearch] = useState('');
  const [riskFilter, setRiskFilter] = useState<'all' | ReliabilityRow['risk_level']>('all');
  const [sortDesc, setSortDesc] = useState(true);

  useEffect(() => {
    const load = async () => {
      const token = safeStorage.getItem('access');
      if (!token) return;
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/reliability`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        setRows(await res.json());
      }
    };

    load();
  }, []);

  const filtered = useMemo(() => {
    return rows
      .filter((row) => riskFilter === 'all' || row.risk_level === riskFilter)
      .filter((row) => (row.member_detail?.name ?? '').toLowerCase().includes(search.toLowerCase()))
      .sort((a, b) => sortDesc ? Number(b.final_score) - Number(a.final_score) : Number(a.final_score) - Number(b.final_score));
  }, [rows, riskFilter, search, sortDesc]);

  const chartData = filtered.slice(0, 10).map((row) => ({
    name: row.member_detail?.name ?? String(row.member),
    final: Number(row.final_score),
  }));

  return (
    <div className="flex min-h-screen bg-gray-950 text-white">
      <Sidebar />
      <main className="flex-1 p-8 space-y-8">
        <div className="flex items-center justify-between gap-4 flex-wrap border-b border-gray-800 pb-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <ShieldAlert className="text-emerald-400" />
              Inactivity + Reliability Scoring
            </h1>
            <p className="text-gray-400 mt-2">Identify members at risk using activity, chain, war, and OC consistency.</p>
          </div>
        </div>

        <section className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2 bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center gap-4 justify-between">
              <label className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
                <input className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-10 pr-4 py-3" value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search member" />
              </label>
              <div className="flex items-center gap-3 flex-wrap">
                <select className="bg-gray-800 border border-gray-700 rounded-lg px-4 py-3" value={riskFilter} onChange={(e) => setRiskFilter(e.target.value as 'all' | ReliabilityRow['risk_level'])}>
                  <option value="all">All Risks</option>
                  <option value="highly_reliable">Highly Reliable</option>
                  <option value="stable">Stable</option>
                  <option value="at_risk">At Risk</option>
                  <option value="high_kick_risk">High Kick Risk</option>
                </select>
                <button onClick={() => setSortDesc((current) => !current)} className="inline-flex items-center gap-2 px-4 py-3 rounded-lg bg-gray-800 border border-gray-700 hover:bg-gray-700">
                  <ArrowDownAZ size={16} /> {sortDesc ? 'High → Low' : 'Low → High'}
                </button>
              </div>
            </div>

            <div className="overflow-auto rounded-2xl border border-gray-800">
              <table className="min-w-full text-left">
                <thead className="bg-gray-800 text-gray-300 text-sm uppercase tracking-wider">
                  <tr>
                    <th className="px-4 py-3">Member</th>
                    <th className="px-4 py-3 text-right">Activity</th>
                    <th className="px-4 py-3 text-right">Chain</th>
                    <th className="px-4 py-3 text-right">War</th>
                    <th className="px-4 py-3 text-right">OC</th>
                    <th className="px-4 py-3 text-right">Final</th>
                    <th className="px-4 py-3">Risk</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800 bg-gray-950/60">
                  {filtered.map((row) => (
                    <tr key={row.id} className="hover:bg-gray-800/50 transition-colors">
                      <td className="px-4 py-3 font-medium">{row.member_detail?.name ?? row.member}</td>
                      <td className="px-4 py-3 text-right">{Number(row.activity_score).toFixed(2)}</td>
                      <td className="px-4 py-3 text-right">{Number(row.chain_score).toFixed(2)}</td>
                      <td className="px-4 py-3 text-right">{Number(row.war_score).toFixed(2)}</td>
                      <td className="px-4 py-3 text-right">{Number(row.oc_score).toFixed(2)}</td>
                      <td className="px-4 py-3 text-right font-semibold text-emerald-300">{Number(row.final_score).toFixed(2)}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${riskStyles[row.risk_level]}`}>
                          {riskLabels[row.risk_level]}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center gap-2 text-gray-200 font-semibold">
              <Filter size={18} className="text-cyan-400" /> Score Leaderboard
            </div>
            <div className="h-96 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                  <XAxis type="number" stroke="#9ca3af" />
                  <YAxis type="category" dataKey="name" width={100} stroke="#9ca3af" />
                  <Tooltip contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151' }} />
                  <Bar dataKey="final" fill="#34d399" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
