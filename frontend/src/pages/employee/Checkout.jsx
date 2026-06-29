import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { checkout, getActivePaymentQR, submitUTR } from "../../api/endpoints";
import { useCart } from "../../context/CartContext";
import { getLocalDateString } from "../../utils/date";

export default function Checkout() {
  const { items, totalAmount, clearCart } = useCart();
  const [step, setStep] = useState("review"); // review -> pay -> done
  const [order, setOrder] = useState(null);
  const [qr, setQr] = useState(null);
  const [utr, setUtr] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    getActivePaymentQR()
      .then(({ data }) => setQr(data.qr))
      .catch(() => setQr(null));
  }, []);

  async function handlePlaceOrder() {
    setError("");
    setSubmitting(true);
    try {
      const today = getLocalDateString();
      const { data } = await checkout({
        order_date: today,
        items: items.map((i) => ({ menu_item_id: i.menu_item_id, quantity: i.quantity })),
      });
      setOrder(data.order);
      setStep("pay");
    } catch (err) {
      const data = err.response?.data;
      const firstFieldError = data?.errors && Object.values(data.errors)[0];
      setError(
        (Array.isArray(firstFieldError) ? firstFieldError[0] : firstFieldError) ||
          data?.detail ||
          "Could not place order."
      );
    } finally {
      setSubmitting(false);
    }
  }

  async function handleSubmitUTR(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await submitUTR(order.id, utr);
      clearCart();
      setStep("done");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not submit UTR number.");
    } finally {
      setSubmitting(false);
    }
  }

  if (items.length === 0 && step === "review") {
    return (
      <div className="max-w-md mx-auto mt-12 text-center text-gray-600">
        <p>Your cart is empty.</p>
        <button onClick={() => navigate("/menu")} className="text-primary hover:underline mt-2">
          Back to menu
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto mt-8 px-4">
      {error && <p className="bg-red-50 text-red-700 text-sm p-2 rounded mb-3">{error}</p>}

      {step === "review" && (
        <div className="bg-white border border-gray-200 rounded p-4">
          <h1 className="text-lg font-bold mb-3">Order Summary</h1>
          <ul className="divide-y divide-gray-100 mb-3">
            {items.map((i) => (
              <li key={i.menu_item_id} className="flex justify-between py-2 text-sm">
                <span>{i.name} × {i.quantity}</span>
                <span>₹{(i.price * i.quantity).toFixed(2)}</span>
              </li>
            ))}
          </ul>
          <div className="flex justify-between font-semibold border-t border-gray-200 pt-2">
            <span>Total</span>
            <span>₹{totalAmount.toFixed(2)}</span>
          </div>
          <button
            onClick={handlePlaceOrder}
            disabled={submitting}
            className="w-full bg-primary text-white py-2 rounded mt-4 hover:bg-primary-dark disabled:opacity-50"
          >
            {submitting ? "Placing order..." : "Place Order"}
          </button>
        </div>
      )}

      {step === "pay" && order && (
        <div className="bg-white border border-gray-200 rounded p-4">
          <h1 className="text-lg font-bold mb-1">Scan & Pay</h1>
          <p className="text-sm text-gray-500 mb-3">
            Order #{order.id} — Total: ₹{Number(order.total_amount).toFixed(2)}
          </p>

          {qr ? (
            <div className="text-center">
              <img src={qr.qr_image} alt="Payment QR" className="mx-auto w-48 h-48 object-contain border border-gray-200 rounded" />
              {qr.upi_id && <p className="text-sm text-gray-600 mt-2">UPI ID: {qr.upi_id}</p>}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No QR code has been configured yet. Please contact admin.</p>
          )}

          <form onSubmit={handleSubmitUTR} className="mt-4 space-y-2">
            <label className="block text-sm text-gray-700">
              Enter UTR / Transaction Reference Number
            </label>
            <input
              required
              value={utr}
              onChange={(e) => setUtr(e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
              placeholder="e.g. 123456789012"
            />
            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-primary text-white py-2 rounded hover:bg-primary-dark disabled:opacity-50"
            >
              {submitting ? "Submitting..." : "Submit Payment Reference"}
            </button>
          </form>
        </div>
      )}

      {step === "done" && (
        <div className="bg-white border border-gray-200 rounded p-6 text-center">
          <h1 className="text-lg font-bold mb-2">✅ Payment Reference Submitted</h1>
          <p className="text-sm text-gray-600 mb-4">
            Your order is awaiting admin verification. You can track its status in My Orders.
          </p>
          <button
            onClick={() => navigate("/orders")}
            className="bg-primary text-white px-4 py-2 rounded hover:bg-primary-dark"
          >
            View My Orders
          </button>
        </div>
      )}
    </div>
  );
}
