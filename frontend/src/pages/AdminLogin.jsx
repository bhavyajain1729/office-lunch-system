import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const { loginAsAdmin } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      await loginAsAdmin(email, password);
      navigate("/admin");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        "Login failed. Please check your credentials."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 flex items-center justify-center px-4">

      <div className="w-full max-w-5xl bg-white rounded-3xl shadow-2xl overflow-hidden grid md:grid-cols-2">

        <div className="hidden md:flex flex-col justify-center bg-slate-900 text-white p-10">
          <div className="text-7xl mb-6">🛠️</div>

          <h1 className="text-4xl font-bold">
            Admin Portal
          </h1>

          <p className="mt-4 text-slate-300">
            Manage menus, orders, employees and payment verification from one dashboard.
          </p>

          <div className="mt-8 space-y-3">
            <div>✅ Dashboard Insights</div>
            <div>✅ Menu Management</div>
            <div>✅ Order Verification</div>
          </div>
        </div>

        <div className="p-8 md:p-12">

          <h2 className="text-3xl font-bold text-slate-800">
            Admin Login
          </h2>

          <p className="text-slate-500 mt-2">
            Sign in to access the dashboard
          </p>

          {error && (
            <div className="mt-4 bg-red-100 text-red-700 p-3 rounded-lg">
              {error}
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="mt-8 space-y-5"
          >
            <div>
              <label className="block mb-2 text-sm font-medium">
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-slate-700 outline-none"
                placeholder="Enter admin email"
              />
            </div>

            <div>
              <label className="block mb-2 text-sm font-medium">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full border border-slate-300 rounded-xl px-4 py-3 focus:ring-2 focus:ring-slate-700 outline-none"
                placeholder="Enter password"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full bg-slate-900 hover:bg-black text-white font-semibold py-3 rounded-xl transition"
            >
              {submitting ? "Logging In..." : "Login as Admin"}
            </button>
          </form>

          <div className="mt-6 p-4 bg-slate-100 rounded-xl text-sm text-slate-600">
            Admin accounts are managed by the backend and cannot be registered from the website.
          </div>

        </div>
      </div>
    </div>
  );
}