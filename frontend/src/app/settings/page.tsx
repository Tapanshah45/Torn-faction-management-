'use client';
import Sidebar from '@/components/layout/Sidebar';

export default function Settings() {
  return (
    <div className="flex min-h-screen bg-gray-900 text-white">
      <Sidebar />
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-8 border-b border-gray-700 pb-4">Settings & Integrations</h1>

        <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 max-w-2xl">
          <h2 className="text-xl font-semibold mb-6">Discord Integration</h2>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2 text-gray-400">Webhook URL</label>
            <input
              type="text"
              placeholder="https://discord.com/api/webhooks/..."
              className="w-full bg-gray-900 border border-gray-700 rounded-lg p-3 text-white focus:outline-none focus:border-blue-500"
            />
          </div>
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors">
            Save Webhook
          </button>
        </div>
      </main>
    </div>
  );
}
