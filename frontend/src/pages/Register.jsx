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
    setForm((prev) => ({
      ...prev,
      [field]: value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();

    setError("");
    setSubmitting(true);

    try {
      await registerEmployee(form);

      setSuccess(true);

      setTimeout(() => {
        navigate("/login");
      }, 1500);

    } catch (err) {
      const data = err.response?.data;

      const firstFieldError =
        data?.errors &&
        Object.values(data.errors)[0];

      setError(
        (Array.isArray(firstFieldError)
          ? firstFieldError[0]
          : firstFieldError) ||
        data?.detail ||
        "Registration failed."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-orange-100 py-10 px-4">

      <div className="max-w-5xl mx-auto bg-white rounded-3xl shadow-2xl overflow-hidden grid md:grid-cols-2">

        <div className="hidden md:flex flex-col justify-center bg-blue-600 text-white p-10">
          <div className="text-7xl mb-6">🍱</div>

          <h1 className="text-4xl font-bold">
            Join Office Lunch
          </h1>

          <p className="mt-4 text-blue-100">
            Create your employee account and start ordering lunch with ease.
          </p>

          <div className="mt-8 space-y-3">
            <div>✅ Daily Menu Access</div>
            <div>✅ Easy Checkout</div>
            <div>✅ Order Tracking</div>
          </div>
        </div>

        <div className="p-8 md:p-10">

          <h2 className="text-3xl font-bold text-slate-800">
            Employee Registration
          </h2>

          <p className="text-slate-500 mt-2">
            Create your account
          </p>

          {error && (
            <div className="mt-4 bg-red-100 text-red-700 p-3 rounded-lg">
              {error}
            </div>
          )}

          {success && (
            <div className="mt-4 bg-green-100 text-green-700 p-3 rounded-lg">
              Registration successful! Redirecting...
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className="mt-6 grid gap-4"
          >

            <input
              type="text"
              placeholder="Full Name"
              value={form.full_name}
              onChange={(e) =>
                update("full_name", e.target.value)
              }
              className="border rounded-xl px-4 py-3"
              required
            />

            <input
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={(e) =>
                update("email", e.target.value)
              }
              className="border rounded-xl px-4 py-3"
              required
            />

            <input
              type="text"
              placeholder="Employee Code"
              value={form.employee_code}
              onChange={(e) =>
                update("employee_code", e.target.value)
              }
              className="border rounded-xl px-4 py-3"
              required
            />

            <input
              type="text"
              placeholder="Department"
              value={form.department}
              onChange={(e) =>
                update("department", e.target.value)
              }
              className="border rounded-xl px-4 py-3"
              required
            />

            <input
              type="text"
              placeholder="Phone Number"
              value={form.phone_number}
              onChange={(e) =>
                update("phone_number", e.target.value)
              }
              className="border rounded-xl px-4 py-3"
              required
            />

            <input
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={(e) =>
                update("password", e.target.value)
              }
              className="border rounded-xl px-4 py-3"
              required
            />

            <input
              type="password"
              placeholder="Confirm Password"
              value={form.password_confirm}
              onChange={(e) =>
                update("password_confirm", e.target.value)
              }
              className="border rounded-xl px-4 py-3"
              required
            />

            <button
              type="submit"
              disabled={submitting}
              className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-3 font-semibold"
            >
              {submitting
                ? "Creating Account..."
                : "Create Account"}
            </button>
          </form>

          <p className="mt-6 text-center text-slate-600">
            Already have an account?{" "}
            <Link
              to="/login"
              className="text-blue-600 font-semibold"
            >
              Login
            </Link>
          </p>

        </div>
      </div>
    </div>
  );
}