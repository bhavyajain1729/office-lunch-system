import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login");
  }

  return (
    <nav className="sticky top-0 z-50 bg-white shadow-md border-b">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">

          <Link
            to="/"
            className="flex items-center gap-2 text-2xl font-bold text-blue-600"
          >
            🍱 Office Lunch
          </Link>

          <div className="flex items-center gap-6">

            {isAuthenticated && !isAdmin && (
              <>
                <Link
                  to="/menu"
                  className="font-medium text-slate-700 hover:text-blue-600 transition"
                >
                  Menu
                </Link>

                <Link
                  to="/orders"
                  className="font-medium text-slate-700 hover:text-blue-600 transition"
                >
                  My Orders
                </Link>
              </>
            )}

            {isAuthenticated && isAdmin && (
              <>
                <Link
                  to="/admin"
                  className="font-medium text-slate-700 hover:text-blue-600 transition"
                >
                  Dashboard
                </Link>

                <Link
                  to="/admin/menu"
                  className="font-medium text-slate-700 hover:text-blue-600 transition"
                >
                  Menu
                </Link>

                <Link
                  to="/admin/orders"
                  className="font-medium text-slate-700 hover:text-blue-600 transition"
                >
                  Orders
                </Link>
              </>
            )}

            {isAuthenticated ? (
              <div className="flex items-center gap-4">
                <div className="hidden md:block text-sm">
                  <p className="font-semibold text-slate-800">
                    {user?.full_name}
                  </p>
                </div>

                <button
                  onClick={handleLogout}
                  className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  to="/login"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  Employee Login
                </Link>

                <Link
                  to="/admin/login"
                  className="border border-slate-300 px-4 py-2 rounded-lg hover:bg-slate-100 transition"
                >
                  Admin Login
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}