import { useEffect, useState } from "react";
import { getAdminOrders, updateOrderStatus, uploadPaymentQR } from "../../api/endpoints";
import StatusBadge from "../../components/StatusBadge";

const NEXT_ACTIONS = {
  PAYMENT_SUBMITTED: [
    { status: "CONFIRMED", label: "Confirm Payment" },
    { status: "REJECTED", label: "Reject" },
  ],
  CONFIRMED: [
    { status: "COMPLETED", label: "Mark Completed" },
    { status: "CANCELLED", label: "Cancel" },
  ],
  PENDING_PAYMENT: [{ status: "CANCELLED", label: "Cancel" }],
  REJECTED: [{ status: "CANCELLED", label: "Cancel" }],
};

export default function OrderManagement() {
  const [orders, setOrders] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [qrFile, setQrFile] = useState(null);
  const [qrLabel, setQrLabel] = useState("Office Canteen UPI");
  const [qrUpi, setQrUpi] = useState("");

  useEffect(() => {
    loadOrders();
  }, [statusFilter]);

  async function loadOrders() {
    try {
      const { data } = await getAdminOrders(statusFilter ? { status: statusFilter } : {});
      setOrders(data.results || data);
    } catch (err) {
      setError("Could not load orders.");
    }
  }

  async function handleStatusChange(orderId, status) {
    setError("");
    try {
      await updateOrderStatus(orderId, { status });
      setMessage(`Order #${orderId} updated to ${status}.`);
      loadOrders();
    } catch (err) {
      setError(err.response?.data?.detail || "Could not update order status.");
    }
  }

  async function handleUploadQR(e) {
    e.preventDefault();
    if (!qrFile) return;
    setError("");
    try {
      const formData = new FormData();
      formData.append("qr_image", qrFile);
      formData.append("label", qrLabel);
      formData.append("upi_id", qrUpi);
      formData.append("is_active", "true");
      await uploadPaymentQR(formData);
      setMessage("Payment QR code uploaded and activated.");
      setQrFile(null);
    } catch (err) {
      setError("Could not upload QR code.");
    }
  }

  return (
    <div className="max-w-5xl mx-auto mt-6 px-4">
      <h1 className="text-xl font-bold mb-4">Order Management</h1>

      {error && <p className="bg-red-50 text-red-700 text-sm p-2 rounded mb-3">{error}</p>}
      {message && <p className="bg-green-50 text-green-700 text-sm p-2 rounded mb-3">{message}</p>}

      {/* QR upload */}
      <div className="bg-white border border-gray-200 rounded p-4 mb-6">
        <h2 className="font-semibold mb-3">Upload Payment QR Code</h2>
        <form onSubmit={handleUploadQR} className="flex flex-wrap items-end gap-2">
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setQrFile(e.target.files[0])}
            className="text-sm"
          />
          <input
            placeholder="Label"
            value={qrLabel}
            onChange={(e) => setQrLabel(e.target.value)}
            className="border border-gray-300 rounded px-3 py-1.5 text-sm"
          />
          <input
            placeholder="UPI ID"
            value={qrUpi}
            onChange={(e) => setQrUpi(e.target.value)}
            className="border border-gray-300 rounded px-3 py-1.5 text-sm"
          />
          <button
            type="submit"
            className="bg-primary text-white px-4 py-1.5 rounded text-sm hover:bg-primary-dark"
          >
            Upload & Activate
          </button>
        </form>
      </div>

      {/* Filter */}
      <div className="mb-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-gray-300 rounded px-3 py-1.5 text-sm"
        >
          <option value="">All Statuses</option>
          <option value="PENDING_PAYMENT">Pending Payment</option>
          <option value="PAYMENT_SUBMITTED">Payment Submitted</option>
          <option value="CONFIRMED">Confirmed</option>
          <option value="REJECTED">Rejected</option>
          <option value="CANCELLED">Cancelled</option>
          <option value="COMPLETED">Completed</option>
        </select>
      </div>

      {/* Orders list */}
      <div className="space-y-3">
        {orders.length === 0 && <p className="text-gray-500 text-sm">No orders found.</p>}
        {orders.map((order) => (
          <div key={order.id} className="bg-white border border-gray-200 rounded p-4">
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold">
                  Order #{order.id} — {order.employee_name} ({order.employee_department || "—"})
                </p>
                <p className="text-sm text-gray-500">
                  {order.items.map((i) => `${i.item_name} ×${i.quantity}`).join(", ")}
                </p>
                <p className="text-sm text-gray-500">
                  {order.order_date} • ₹{Number(order.total_amount).toFixed(2)}
                  {order.utr_number && ` • UTR: ${order.utr_number}`}
                </p>
              </div>
              <StatusBadge status={order.status} />
            </div>

            {(NEXT_ACTIONS[order.status] || []).length > 0 && (
              <div className="flex gap-2 mt-3">
                {NEXT_ACTIONS[order.status].map((action) => (
                  <button
                    key={action.status}
                    onClick={() => handleStatusChange(order.id, action.status)}
                    className="text-sm bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded"
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
