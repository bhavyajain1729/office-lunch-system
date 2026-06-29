const STATUS_STYLES = {
  PENDING_PAYMENT: "bg-yellow-100 text-yellow-800",
  PAYMENT_SUBMITTED: "bg-blue-100 text-blue-800",
  CONFIRMED: "bg-green-100 text-green-800",
  REJECTED: "bg-red-100 text-red-800",
  CANCELLED: "bg-gray-100 text-gray-600",
  COMPLETED: "bg-purple-100 text-purple-800",
};

const STATUS_LABELS = {
  PENDING_PAYMENT: "Pending Payment",
  PAYMENT_SUBMITTED: "Payment Submitted",
  CONFIRMED: "Confirmed",
  REJECTED: "Rejected",
  CANCELLED: "Cancelled",
  COMPLETED: "Completed",
};

export default function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] || "bg-gray-100 text-gray-600";
  const label = STATUS_LABELS[status] || status;
  return (
    <span className={`inline-block px-2 py-1 rounded text-xs font-medium ${style}`}>
      {label}
    </span>
  );
}
