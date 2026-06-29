import { useEffect, useState } from "react";
import { getMyOrders } from "../../api/endpoints";
import StatusBadge from "../../components/StatusBadge";

export default function OrderHistory() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getMyOrders()
      .then(({ data }) => setOrders(data.results || data))
      .catch(() => setError("Could not load your orders."))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-center mt-10 text-gray-500">Loading orders...</p>;
  if (error) return <p className="text-center mt-10 text-red-600">{error}</p>;

  return (
    <div className="max-w-3xl mx-auto mt-6 px-4">
      <h1 className="text-xl font-bold mb-4">My Orders</h1>

      {orders.length === 0 ? (
        <p className="text-gray-500">You haven't placed any orders yet.</p>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => (
            <div key={order.id} className="bg-white border border-gray-200 rounded p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-semibold">Order #{order.id} — {order.order_date}</p>
                  <p className="text-sm text-gray-500">
                    {order.items.map((i) => `${i.item_name} ×${i.quantity}`).join(", ")}
                  </p>
                </div>
                <StatusBadge status={order.status} />
              </div>
              <div className="flex justify-between items-center mt-2 text-sm">
                <span>Total: ₹{Number(order.total_amount).toFixed(2)}</span>
                {order.utr_number && <span className="text-gray-500">UTR: {order.utr_number}</span>}
              </div>
              {order.admin_remarks && (
                <p className="text-xs text-gray-500 mt-1">Admin note: {order.admin_remarks}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
