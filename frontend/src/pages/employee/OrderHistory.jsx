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

  if (loading) {
    return (
      <div className="p-10 text-center">
        Loading orders...
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-red-100 text-red-700 rounded-xl p-4">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">

      <h1 className="text-4xl font-bold text-slate-800 mb-8">
        My Orders
      </h1>

      {orders.length === 0 ? (
        <div className="bg-white rounded-2xl shadow p-10 text-center">
          <div className="text-6xl mb-4">🍱</div>
          <p className="text-slate-500">
            You haven't placed any orders yet.
          </p>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <div
              key={order.id}
              className="bg-white rounded-2xl shadow-lg p-6 border"
            >
              <div className="flex flex-wrap justify-between gap-4">

                <div>
                  <h2 className="font-bold text-xl">
                    Order #{order.id}
                  </h2>

                  <p className="text-slate-500">
                    {order.order_date}
                  </p>
                </div>

                <StatusBadge status={order.status} />
              </div>

              <div className="mt-4">
                <h3 className="font-semibold mb-2">
                  Items
                </h3>

                <div className="space-y-2">
                  {order.items.map((item) => (
                    <div
                      key={item.id}
                      className="flex justify-between border-b pb-2"
                    >
                      <span>
                        {item.item_name} × {item.quantity}
                      </span>

                      <span>
                        ₹
                        {(
                          item.unit_price * item.quantity
                        ).toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="mt-4 flex justify-between font-bold text-lg">
                <span>Total</span>
                <span>
                  ₹{Number(order.total_amount).toFixed(2)}
                </span>
              </div>

              {order.utr_number && (
                <div className="mt-4 text-sm text-slate-600">
                  UTR: ******{order.utr_number.slice(-4)}
                </div>
              )}

              {order.admin_remarks && (
                <div className="mt-4 bg-yellow-100 text-yellow-800 rounded-lg p-3">
                  Admin Note: {order.admin_remarks}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}