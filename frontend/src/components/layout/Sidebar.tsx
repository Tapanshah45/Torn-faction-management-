'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Users, Link as LinkIcon, Swords, AlertTriangle, Settings, ShieldAlert, Landmark, Gauge } from 'lucide-react';
import clsx from 'clsx';
import { safeStorage } from '@/lib/safeStorage';

const navItems = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Members', href: '/members', icon: Users },
  { name: 'Live Chain', href: '/chain', icon: LinkIcon },
  { name: 'War Analytics', href: '/wars', icon: Swords },
  { name: 'Organized Crimes', href: '/crimes', icon: ShieldAlert },
  { name: 'Payouts', href: '/payouts', icon: Landmark },
  { name: 'Reliability', href: '/reliability', icon: Gauge },
  { name: 'Alerts', href: '/alerts', icon: AlertTriangle },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 bg-gray-800 text-white min-h-screen p-4 flex flex-col">
      <h2 className="text-2xl font-bold mb-8 text-center border-b border-gray-700 pb-4">War Room</h2>
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link key={item.name} href={item.href}>
              <span className={clsx(
                "flex items-center space-x-3 p-3 rounded-lg transition-colors cursor-pointer",
                isActive ? "bg-blue-600 text-white" : "text-gray-400 hover:bg-gray-700 hover:text-white"
              )}>
                <Icon size={20} />
                <span className="font-medium">{item.name}</span>
              </span>
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto border-t border-gray-700 pt-4">
        <button
          onClick={() => {
            safeStorage.removeItem('access');
            safeStorage.removeItem('refresh');
            window.location.href = '/login';
          }}
          className="w-full text-left p-3 text-red-400 hover:bg-gray-700 hover:text-red-300 rounded-lg transition-colors"
        >
          Logout
        </button>
      </div>
    </div>
  );
}
