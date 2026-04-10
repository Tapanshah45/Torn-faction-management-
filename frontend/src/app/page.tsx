'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/layout/Sidebar';
import { safeStorage } from '@/lib/safeStorage';
import { Users, UserCheck, Clock, Link as LinkIcon, Swords, Target, AlertTriangle, ShieldAlert } from 'lucide-react';

interface DashboardData {
  total_members: number;
  online_members: number;
  active_1h: string | number;
  active_24h: string | number;
  current_chain: string | number;
  active_war: string;
  respect_today: number;
  inactive_members: number;
  ongoing_ocs: number;
}

export default function Dashboard() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    const token = safeStorage.getItem('access');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchDashboard = async () => {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          const result = await res.json();
          setData(result);
        } else if (res.status === 401) {
          router.push('/login');
        }
      } catch (err) {
        console.error("Error fetching dashboard", err);
      }
    };

    fetchDashboard();
    const interval = setInterval(async () => {
      const token = safeStorage.getItem('access');
      if (!token) {
        clearInterval(interval);
        router.push('/login');
        return;
      }
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL}/api/dashboard/`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (res.status === 401) {
          clearInterval(interval);
          router.push('/login');
          return;
        }
        if (res.ok) {
          setData(await res.json());
        }
      } catch (err) {
        console.error('Dashboard refresh error', err);
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [router]);

  if (!data) return <div className="min-h-screen bg-gray-900 flex items-center justify-center text-white">Loading...</div>;

  const cards = [
    { title: 'Total Members', value: data.total_members, icon: Users, color: 'text-blue-400' },
    { title: 'Online Now', value: data.online_members, icon: UserCheck, color: 'text-green-400' },
    { title: 'Active (1h)', value: data.active_1h, icon: Clock, color: 'text-yellow-400' },
    { title: 'Active (24h)', value: data.active_24h, icon: Clock, color: 'text-orange-400' },
    { title: 'Current Chain', value: data.current_chain, icon: LinkIcon, color: 'text-purple-400' },
    { title: 'Active War', value: data.active_war, icon: Swords, color: 'text-red-400' },
    { title: 'Respect Today', value: data.respect_today, icon: Target, color: 'text-pink-400' },
    { title: 'Inactive Alerts', value: data.inactive_members, icon: AlertTriangle, color: 'text-red-500' },
    { title: 'Ongoing OCs', value: data.ongoing_ocs, icon: ShieldAlert, color: 'text-indigo-400' },
  ];

  return (
    <div className="flex min-h-screen bg-gray-900">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 text-white border-b border-gray-700 pb-4">Command Center</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div key={idx} className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-sm hover:border-gray-600 transition-all">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-gray-400 font-medium">{card.title}</h3>
                  <Icon className={card.color} size={24} />
                </div>
                <p className="text-3xl font-bold text-white">{card.value}</p>
              </div>
            );
          })}
        </div>
      </main>
    </div>
  );
}
