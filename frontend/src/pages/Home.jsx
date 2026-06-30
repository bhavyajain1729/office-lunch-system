import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { isAuthenticated, isAdmin } = useAuth();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-orange-50">

      <section className="max-w-7xl mx-auto px-6 py-20">

        <div className="grid lg:grid-cols-2 gap-12 items-center">

          <div>
            <span className="inline-block bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold">
              Office Lunch Management System
            </span>

            <h1 className="mt-6 text-5xl lg:text-6xl font-extrabold leading-tight text-slate-800">
              Order Your
              <span className="text-blue-600"> Office Lunch </span>
              In Seconds 🍱
            </h1>

            <p className="mt-6 text-lg text-slate-600 leading-relaxed">
              Manage employee lunch orders, payments, menu planning and
              order tracking from one modern platform.
            </p>

            <div className="mt-8 flex flex-wrap gap-4">
              {!isAuthenticated ? (
                <>
                  <Link
                    to="/login"
                    className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold shadow hover:bg-blue-700 transition"
                  >
                    Employee Login
                  </Link>

                  <Link
                    to="/register"
                    className="border border-slate-300 px-6 py-3 rounded-xl font-semibold hover:bg-slate-100 transition"
                  >
                    Register
                  </Link>

                  <Link
                    to="/admin/login"
                    className="bg-slate-800 text-white px-6 py-3 rounded-xl font-semibold hover:bg-slate-900 transition"
                  >
                    Admin Login
                  </Link>
                </>
              ) : (
                <Link
                  to={isAdmin ? "/admin" : "/menu"}
                  className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold"
                >
                  {isAdmin ? "Go To Dashboard" : "View Today's Menu"}
                </Link>
              )}
            </div>
          </div>

          <div>
            <div className="bg-white rounded-3xl shadow-xl p-8">

              <div className="text-center text-8xl">
                🍱
              </div>

              <div className="mt-8 grid grid-cols-2 gap-4">

                <div className="bg-blue-50 rounded-xl p-5">
                  <h3 className="font-bold text-blue-600">Fast Ordering</h3>
                  <p className="text-sm text-slate-600 mt-2">
                    Order lunch in less than a minute.
                  </p>
                </div>

                <div className="bg-green-50 rounded-xl p-5">
                  <h3 className="font-bold text-green-600">
                    Secure Payments
                  </h3>
                  <p className="text-sm text-slate-600 mt-2">
                    UPI QR powered payments.
                  </p>
                </div>

                <div className="bg-orange-50 rounded-xl p-5">
                  <h3 className="font-bold text-orange-600">
                    Order Tracking
                  </h3>
                  <p className="text-sm text-slate-600 mt-2">
                    Track every order status.
                  </p>
                </div>

                <div className="bg-purple-50 rounded-xl p-5">
                  <h3 className="font-bold text-purple-600">
                    Admin Dashboard
                  </h3>
                  <p className="text-sm text-slate-600 mt-2">
                    Complete management system.
                  </p>
                </div>

              </div>

            </div>
          </div>

        </div>
      </section>

    </div>
  );
}