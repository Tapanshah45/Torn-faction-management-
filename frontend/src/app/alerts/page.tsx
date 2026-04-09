'use client';
import { useEffect, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import { AlertTriangle } from 'lucide-react';

interface Alert {
  id: number;
  alert_type: string;
  created_at: string;
  member_detail?: { name: string };
}

export default function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      const token = localStorage.getItem('access');
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/alerts/`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          setAlerts(await res.json());
        }
      } catch (err) {
        console.error(err);
      }
    };
    fetchAlerts();
  }, []);

  return (
    <div className="flex min-h-screen bg-gray-900 text-white">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 border-b border-gray-700 pb-4">Activity Alerts</h1>
        <div className="space-y-4">
          {alerts.length === 0 ? (
            <div className="bg-gray-800 p-6 rounded-lg text-center text-gray-500 border border-gray-700">
              No active alerts.
            </div>
          ) : (
            alerts.map((alert: Alert) => (
              <div key={alert.id} className="bg-gray-800 p-4 rounded-lg border border-l-4 border-l-red-500 flex items-start gap-4">
                <AlertTriangle className="text-red-500 mt-1" />
                <div>
                  <h3 className="font-semibold text-lg">{alert.alert_type}</h3>
                  <p className="text-gray-400">Member: {alert.member_detail?.name || 'Unknown'}</p>
                  <p className="text-sm text-gray-500 mt-2">{new Date(alert.created_at).toLocaleString()}</p>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
    </div>
  );
}
