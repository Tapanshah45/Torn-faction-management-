'use client';
import { useEffect, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';

interface Member {
  id: number;
  name: string;
  torn_player_id: number;
  faction_rank: string;
  level: number;
  status: string;
}

export default function Members() {
  const [members, setMembers] = useState<Member[]>([]);

  useEffect(() => {
    const fetchMembers = async () => {
      const token = localStorage.getItem('access');
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/members/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          setMembers(await res.json());
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchMembers();
  }, []);

  return (
    <div className="flex min-h-screen bg-gray-900 text-white">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 border-b border-gray-700 pb-4">Member Activity Management</h1>
        <div className="bg-gray-800 rounded-lg shadow border border-gray-700 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-700 text-gray-300">
              <tr>
                <th className="p-4 font-medium">Name [ID]</th>
                <th className="p-4 font-medium">Rank</th>
                <th className="p-4 font-medium">Level</th>
                <th className="p-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {members.length === 0 ? (
                <tr><td colSpan={4} className="p-4 text-center text-gray-500">No members found.</td></tr>
              ) : (
                members.map((m: Member) => (
                  <tr key={m.id} className="hover:bg-gray-750 transition-colors">
                    <td className="p-4">{m.name} [{m.torn_player_id}]</td>
                    <td className="p-4">{m.faction_rank}</td>
                    <td className="p-4">{m.level}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${m.status === 'Online' ? 'bg-green-900 text-green-300' : 'bg-gray-600 text-gray-300'}`}>
                        {m.status || 'Unknown'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
