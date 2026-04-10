'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import { safeStorage } from '@/lib/safeStorage';
import { Calculator, Download, Search, ShieldCheck, Swords, TriangleAlert } from 'lucide-react';

type WarOption = {
  war_id: string;
  participants: number;
  total_hits: number;
  total_respect: string;
  is_active: boolean;
  last_timestamp: string | null;
};

type ContributionRow = {
  member_id: number;
  member_name: string;
  total_hits: number;
  total_respect: string;
};

type PayoutMember = {
  id: number;
  member: number;
  name: string;
  hits: number;
  respect: string;
  share_percent: string;
  payout: string;
};

type PayoutResult = {
  id: number;
  war_id: string;
  mode: 'hits' | 'respect';
  total_pool: string;
  faction_cut: string;
  distributable_pool: string;
  created_at: string;
  members: PayoutMember[];
};

type SortKey = 'payout' | 'hits' | 'respect';

const SORT_LABELS: Record<SortKey, string> = {
  payout: 'Payout High to Low',
  hits: 'Hits High to Low',
  respect: 'Respect High to Low',
};

export default function PayoutsPage() {
  const token = safeStorage.getItem('access');

  const [wars, setWars] = useState<WarOption[]>([]);
  const [selectedWarId, setSelectedWarId] = useState('');
  const [manualWarId, setManualWarId] = useState('');
  const [warPreview, setWarPreview] = useState<ContributionRow[]>([]);
  const [history, setHistory] = useState<PayoutResult[]>([]);

  const [totalPool, setTotalPool] = useState('500000000');
  const [factionCut, setFactionCut] = useState('10');
  const [payoutMode, setPayoutMode] = useState<'hits' | 'respect'>('hits');
  const [sortBy, setSortBy] = useState<SortKey>('payout');

  const [result, setResult] = useState<PayoutResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingWarData, setLoadingWarData] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadWarList = useCallback(async () => {
    if (!token) return;
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payouts/wars`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!res.ok) {
      setError('Failed to load ranked wars list. Check your API connection.');
      return;
    }

    const data: WarOption[] = await res.json();
    setWars(data);

    if (!selectedWarId && data.length > 0) {
      const active = data.find((war) => war.is_active) ?? data[0];
      setSelectedWarId(active.war_id);
      setManualWarId(active.war_id);
    }
  }, [token]);

  const loadHistory = useCallback(async () => {
    if (!token) return;
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payouts/history`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      setHistory(await res.json());
    }
  }, [token]);

  useEffect(() => {
    loadWarList();
    loadHistory();
  }, [loadWarList, loadHistory]);

  const loadWarContributions = useCallback(async (warId: string) => {
    if (!token || !warId) return;
    setLoadingWarData(true);
    setError(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payouts/war-contributions/${encodeURIComponent(warId)}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) {
        const message = await res.json().catch(() => ({ detail: 'Unable to fetch war contributions.' }));
        throw new Error(message.detail ?? 'Unable to fetch war contributions.');
      }

      const data = await res.json();
      setWarPreview(data.members ?? []);
      setSelectedWarId(warId);
      setManualWarId(warId);
    } catch (err) {
      setWarPreview([]);
      setError(err instanceof Error ? err.message : 'Unable to fetch war contributions.');
    } finally {
      setLoadingWarData(false);
    }
  }, [token]);

  useEffect(() => {
    if (selectedWarId) {
      loadWarContributions(selectedWarId);
    }
  }, [selectedWarId, loadWarContributions]);

  const sortedMembers = useMemo(() => {
    if (!result) return [];

    return [...result.members].sort((a, b) => {
      if (sortBy === 'hits') return b.hits - a.hits;
      if (sortBy === 'respect') return Number(b.respect) - Number(a.respect);
      return Number(b.payout) - Number(a.payout);
    });
  }, [result, sortBy]);

  const validate = (): string | null => {
    const pool = Number(totalPool);
    const cut = Number(factionCut);

    if (!selectedWarId) {
      return 'Please select a Ranked War.';
    }
    if (!Number.isFinite(pool) || pool <= 0) {
      return 'Total pool must be greater than zero.';
    }
    if (!Number.isFinite(cut) || cut < 0 || cut > 100) {
      return 'Faction cut must be between 0 and 100.';
    }
    return null;
  };

  const calculate = async () => {
    if (!token) return;
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/payouts/calculate`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          war_id: selectedWarId,
          total_pool: totalPool,
          faction_cut: factionCut,
          payout_mode: payoutMode,
        }),
      });

      if (!res.ok) {
        const message = await res.json().catch(() => ({ detail: 'Failed to generate payout sheet.' }));
        throw new Error(message.detail ?? 'Failed to generate payout sheet.');
      }

      const payload: PayoutResult = await res.json();
      setResult(payload);
      await loadHistory();
    } catch (err) {
      setResult(null);
      setError(err instanceof Error ? err.message : 'Failed to generate payout sheet.');
    } finally {
      setLoading(false);
    }
  };

  const exportCsv = () => {
    if (!result) return;

    const lines = [
      'member_name,hits,respect,share,payout',
      ...sortedMembers.map((row) => [
        JSON.stringify(row.name),
        row.hits,
        row.respect,
        row.share_percent,
        row.payout,
      ].join(',')),
    ];

    const blob = new Blob([lines.join('\n')], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ranked-war-payout-${result.war_id}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex min-h-screen bg-gray-950 text-white">
      <Sidebar />
      <main className="flex-1 p-6 md:p-8 space-y-8">
        <div className="border-b border-gray-800 pb-4 flex items-start justify-between gap-4 flex-wrap">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Calculator className="text-cyan-400" />
              Ranked War Payout Calculator
            </h1>
            <p className="text-gray-400 mt-2">Automated payouts from Ranked War logs. No manual member hit/respect entry required.</p>
          </div>
          {result && (
            <button
              onClick={exportCsv}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 hover:bg-cyan-500 transition-colors font-medium"
            >
              <Download size={16} /> Export CSV
            </button>
          )}
        </div>

        {error && (
          <div className="rounded-xl border border-red-700 bg-red-950/50 px-4 py-3 text-red-200 flex items-center gap-2">
            <TriangleAlert size={16} /> {error}
          </div>
        )}

        <section className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2 rounded-2xl border border-gray-800 bg-gray-900 p-6 space-y-5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="space-y-2 md:col-span-2">
                <span className="text-sm text-gray-400">Select Ranked War</span>
                <select
                  value={selectedWarId}
                  onChange={(event) => setSelectedWarId(event.target.value)}
                  className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3"
                >
                  <option value="">Select a war</option>
                  {wars.map((war) => (
                    <option key={war.war_id} value={war.war_id}>
                      {war.is_active ? 'Active' : 'Previous'} | {war.war_id} | hits {war.total_hits} | members {war.participants}
                    </option>
                  ))}
                </select>
              </label>

              <label className="space-y-2 md:col-span-2">
                <span className="text-sm text-gray-400">Manual War ID Search</span>
                <div className="flex items-center gap-2">
                  <input
                    value={manualWarId}
                    onChange={(event) => setManualWarId(event.target.value)}
                    className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3"
                    placeholder="Enter war id"
                  />
                  <button
                    onClick={() => loadWarContributions(manualWarId.trim())}
                    className="inline-flex items-center gap-2 rounded-lg bg-gray-700 px-4 py-3 hover:bg-gray-600"
                  >
                    <Search size={16} /> Load
                  </button>
                </div>
              </label>

              <label className="space-y-2">
                <span className="text-sm text-gray-400">Total Reward Pool</span>
                <input
                  value={totalPool}
                  onChange={(event) => setTotalPool(event.target.value)}
                  className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3"
                  inputMode="numeric"
                />
              </label>

              <label className="space-y-2">
                <span className="text-sm text-gray-400">Faction Cut %</span>
                <input
                  value={factionCut}
                  onChange={(event) => setFactionCut(event.target.value)}
                  className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-3"
                  inputMode="decimal"
                />
              </label>
            </div>

            <div className="rounded-xl border border-gray-700 bg-gray-800/60 p-4 space-y-3">
              <p className="text-sm text-gray-300">Payout Mode</p>
              <div className="flex items-center gap-6 flex-wrap">
                <label className="inline-flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="payout_mode"
                    value="hits"
                    checked={payoutMode === 'hits'}
                    onChange={() => setPayoutMode('hits')}
                  />
                  Payout by Hits
                </label>
                <label className="inline-flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="payout_mode"
                    value="respect"
                    checked={payoutMode === 'respect'}
                    onChange={() => setPayoutMode('respect')}
                  />
                  Payout by Respect
                </label>
              </div>
            </div>

            <button
              onClick={calculate}
              disabled={loading}
              className="inline-flex items-center gap-2 rounded-xl bg-cyan-600 px-5 py-3 font-semibold hover:bg-cyan-500 disabled:opacity-50"
            >
              <ShieldCheck size={18} />
              {loading ? 'Generating...' : 'Generate Payout Sheet'}
            </button>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border border-gray-800 bg-gray-900 p-6 space-y-3">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <Swords className="text-amber-400" size={18} />
                Selected War Preview
              </h2>
              {loadingWarData ? (
                <p className="text-gray-400 text-sm">Loading war contributions...</p>
              ) : warPreview.length > 0 ? (
                <>
                  <p className="text-sm text-gray-400">Members: {warPreview.length}</p>
                  <p className="text-sm text-gray-400">
                    Total Hits: {warPreview.reduce((sum, row) => sum + row.total_hits, 0).toLocaleString()}
                  </p>
                  <p className="text-sm text-gray-400">
                    Total Respect: {warPreview.reduce((sum, row) => sum + Number(row.total_respect), 0).toLocaleString()}
                  </p>
                </>
              ) : (
                <p className="text-gray-500 text-sm">No contribution data loaded for this war yet.</p>
              )}
            </div>

            <div className="rounded-2xl border border-gray-800 bg-gray-900 p-6 space-y-3">
              <h2 className="text-xl font-semibold">Payout History</h2>
              <div className="space-y-3 max-h-[20rem] overflow-auto">
                {history.slice(0, 6).map((entry) => (
                  <div key={entry.id} className="rounded-lg border border-gray-800 bg-gray-950/70 p-3 text-sm">
                    <p className="font-semibold">War {entry.war_id}</p>
                    <p className="text-gray-400">Mode: {entry.mode}</p>
                    <p className="text-gray-400">Pool: {Number(entry.total_pool).toLocaleString()}</p>
                    <p className="text-gray-400">Cut: {entry.faction_cut}%</p>
                  </div>
                ))}
                {history.length === 0 && <p className="text-gray-500 text-sm">No payouts yet.</p>}
              </div>
            </div>
          </div>
        </section>

        {result && (
          <section className="rounded-2xl border border-gray-800 bg-gray-900 p-6">
            <div className="flex items-center justify-between gap-3 flex-wrap mb-4">
              <h2 className="text-xl font-semibold">Payout Sheet</h2>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-400">Sort:</span>
                <select
                  value={sortBy}
                  onChange={(event) => setSortBy(event.target.value as SortKey)}
                  className="rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm"
                >
                  {(Object.keys(SORT_LABELS) as SortKey[]).map((key) => (
                    <option value={key} key={key}>{SORT_LABELS[key]}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mb-4 grid grid-cols-1 md:grid-cols-4 gap-3 text-sm">
              <div className="rounded-lg border border-gray-800 bg-gray-950/60 p-3">War: <span className="font-semibold">{result.war_id}</span></div>
              <div className="rounded-lg border border-gray-800 bg-gray-950/60 p-3">Mode: <span className="font-semibold">{result.mode}</span></div>
              <div className="rounded-lg border border-gray-800 bg-gray-950/60 p-3">Pool: <span className="font-semibold">{Number(result.total_pool).toLocaleString()}</span></div>
              <div className="rounded-lg border border-gray-800 bg-gray-950/60 p-3">Distributable: <span className="font-semibold text-cyan-300">{Number(result.distributable_pool).toLocaleString()}</span></div>
            </div>

            <div className="overflow-auto">
              <table className="min-w-full text-left">
                <thead className="bg-gray-800 text-gray-300 text-sm uppercase tracking-wider">
                  <tr>
                    <th className="px-4 py-3">Member</th>
                    <th className="px-4 py-3 text-right">Hits</th>
                    <th className="px-4 py-3 text-right">Respect</th>
                    <th className="px-4 py-3 text-right">Share %</th>
                    <th className="px-4 py-3 text-right">Final Payout</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {sortedMembers.map((row) => (
                    <tr key={row.id} className="hover:bg-gray-800/60">
                      <td className="px-4 py-3">{row.name}</td>
                      <td className="px-4 py-3 text-right">{row.hits.toLocaleString()}</td>
                      <td className="px-4 py-3 text-right">{Number(row.respect).toLocaleString()}</td>
                      <td className="px-4 py-3 text-right">{Number(row.share_percent).toFixed(2)}%</td>
                      <td className="px-4 py-3 text-right font-semibold text-cyan-300">{Number(row.payout).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
