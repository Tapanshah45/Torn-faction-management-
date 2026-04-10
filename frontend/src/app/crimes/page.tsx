'use client';
import { useEffect, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import { safeStorage } from '@/lib/safeStorage';
import { ShieldAlert, CheckCircle, XCircle } from 'lucide-react';

interface Crime {
  id: number;
  crime_name: string;
  member_name: string;
  role: string;
  success: boolean;
  timestamp: string;
}

export default function Crimes() {
  const [crimes, setCrimes] = useState<Crime[]>([]);

  useEffect(() => {
    const fetchCrimes = async () => {
      const token = safeStorage.getItem('access');
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/organized-crimes/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          setCrimes(await res.json());
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchCrimes();
  }, []);

  return (
    <div className="flex min-h-screen bg-gray-900 text-white">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 border-b border-gray-700 pb-4 flex items-center gap-3">
          <ShieldAlert className="text-indigo-400" />
          Organized Crime Tracker
        </h1>
        <div className="bg-gray-800 rounded-lg shadow border border-gray-700 overflow-hidden">
          <table className="w-full text-left">
            <thead className="bg-gray-700 text-gray-300">
              <tr>
                <th className="p-4 font-medium">Crime Name</th>
                <th className="p-4 font-medium">Member</th>
                <th className="p-4 font-medium">Role</th>
                <th className="p-4 font-medium">Status</th>
                <th className="p-4 font-medium">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {crimes.length === 0 ? (
                <tr><td colSpan={5} className="p-4 text-center text-gray-500">No organized crimes found.</td></tr>
              ) : (
                crimes.map((c: Crime) => (
                  <tr key={c.id} className="hover:bg-gray-750 transition-colors">
                    <td className="p-4 font-medium">{c.crime_name}</td>
                    <td className="p-4">{c.member_name}</td>
                    <td className="p-4">{c.role}</td>
                    <td className="p-4">
                      {c.success ? (
                        <span className="flex items-center gap-1 text-green-400"><CheckCircle size={16} /> Success</span>
                      ) : (
                        <span className="flex items-center gap-1 text-red-400"><XCircle size={16} /> Failed</span>
                      )}
                    </td>
                    <td className="p-4 text-sm text-gray-400">{new Date(c.timestamp).toLocaleString()}</td>
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
