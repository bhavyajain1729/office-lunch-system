import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { registerEmployee } from "../api/endpoints";

export default function Register() {
  const [form, setForm] = useState({
    email: "",
    full_name: "",
    employee_code: "",
    department: "",
    phone_number: "",
    password: "",
    password_confirm: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  function update(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      await registerEmployee(form);
      setSuccess(true);
      setTimeout(() => navigate("/login"), 1500);
    } catch (err) {
      const data = err.response?.data;
      const firstFieldError = data?.errors && Object.values(data.errors)[0];
      setError(
        (Array.isArray(firstFieldError) ? firstFieldError[0] : firstFieldError) ||
          data?.detail ||
          "Registration failed."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-md mx-auto mt-12 bg-white border border-gray-200 rounded p-6">
      <h1 className="text-xl font-bold mb-4">Employee Sign Up</h1>
      {error && <p className="bg-red-50 text-red-700 text-sm p-2 rounded mb-3">{error}</p>}
      {success && (
        <p className="bg-green-50 text-green-700 text-sm p-2 rounded mb-3">
          Registered successfully! Redirecting to login...
        </p>
      )}
      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-sm text-gray-700 mb-1">Full Name</label>
          <input
            required
            value={form.full_name}
            onChange={(e) => update("full_name", e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-700 mb-1">Email</label>
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => update("email", e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm text-gray-700 mb-1">Employee Code</label>
            <input
              value={form.employee_code}
              onChange={(e) => update("employee_code", e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-700 mb-1">Department</label>
            <input
              value={form.department}
              onChange={(e) => update("department", e.target.value)}
              className="w-full border border-gray-300 rounded px-3 py-2"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm text-gray-700 mb-1">Phone Number</label>
          <input
            value={form.phone_number}
            onChange={(e) => update("phone_number", e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-700 mb-1">Password</label>
          <input
            type="password"
            required
            value={form.password}
            onChange={(e) => update("password", e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm text-gray-700 mb-1">Confirm Password</label>
          <input
            type="password"
            required
            value={form.password_confirm}
            onChange={(e) => update("password_confirm", e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-2"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="w-full bg-primary text-white py-2 rounded hover:bg-primary-dark disabled:opacity-50"
        >
          {submitting ? "Creating account..." : "Sign Up"}
        </button>
      </form>
      <p className="text-sm text-gray-600 mt-4">
        Already have an account?{" "}
        <Link to="/login" className="text-primary hover:underline">Login</Link>
      </p>
    </div>
  );
}
