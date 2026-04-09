'use client';
import Sidebar from '@/components/layout/Sidebar';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Wars() {
  const data = [
    { time: '12:00', respect: 100 },
    { time: '13:00', respect: 250 },
    { time: '14:00', respect: 350 },
    { time: '15:00', respect: 500 },
  ];

  return (
    <div className="flex min-h-screen bg-gray-900 text-white">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 border-b border-gray-700 pb-4">War Analytics</h1>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 mb-8 flex flex-col">
          <h2 className="text-xl font-semibold mb-6">Respect Trend</h2>
          <div className="h-80 w-full min-w-0 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
                <Line type="monotone" dataKey="respect" stroke="#F87171" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </main>
    </div>
  );
}
