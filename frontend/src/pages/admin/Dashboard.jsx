import { useEffect, useState } from "react";
import { getAdminDashboard } from "../../api/endpoints";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAdminDashboard()
      .then(({ data }) => setStats(data))
      .catch(() => setError("Could not load dashboard stats."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-center mt-10 text-gray-500">Loading dashboard...</p>;
  if (error) return <p className="text-center mt-10 text-red-600">{error}</p>;

  return (
    <div className="max-w-4xl mx-auto mt-6 px-4">
      <h1 className="text-xl font-bold mb-1">Admin Dashboard</h1>
      <p className="text-sm text-gray-500 mb-6">Stats for {stats.date}</p>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Orders" value={stats.total_orders} />
        <StatCard label="Pending Verification" value={stats.pending_verification} />
        <StatCard label="Confirmed Revenue" value={`₹${Number(stats.confirmed_revenue).toFixed(2)}`} />
        <StatCard label="Statuses" value={Object.keys(stats.status_breakdown).length} />
      </div>

      <div className="bg-white border border-gray-200 rounded p-4 mb-6">
        <h2 className="font-semibold mb-2">Status Breakdown</h2>
        <ul className="text-sm space-y-1">
          {Object.entries(stats.status_breakdown).map(([status, count]) => (
            <li key={status} className="flex justify-between">
              <span>{status}</span>
              <span>{count}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="bg-white border border-gray-200 rounded p-4">
        <h2 className="font-semibold mb-2">Top Items Today</h2>
        {stats.top_items.length === 0 ? (
          <p className="text-sm text-gray-500">No orders yet today.</p>
        ) : (
          <ul className="text-sm space-y-1">
            {stats.top_items.map((item) => (
              <li key={item.item_name} className="flex justify-between">
                <span>{item.item_name}</span>
                <span>{item.quantity}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="bg-white border border-gray-200 rounded p-4 text-center">
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-xs text-gray-500 mt-1">{label}</p>
    </div>
  );
}
