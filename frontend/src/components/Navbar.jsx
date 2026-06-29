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
    <nav className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      <Link to="/" className="text-lg font-bold text-primary">
        🍱 Office Lunch
      </Link>

      <div className="flex items-center gap-4 text-sm">
        {isAuthenticated && !isAdmin && (
          <>
            <Link to="/menu" className="hover:text-primary">Menu</Link>
            <Link to="/orders" className="hover:text-primary">My Orders</Link>
          </>
        )}
        {isAuthenticated && isAdmin && (
          <>
            <Link to="/admin" className="hover:text-primary">Dashboard</Link>
            <Link to="/admin/menu" className="hover:text-primary">Menu Management</Link>
            <Link to="/admin/orders" className="hover:text-primary">Order Management</Link>
          </>
        )}

        {isAuthenticated ? (
          <div className="flex items-center gap-3">
            <span className="text-gray-600">{user?.full_name}</span>
            <button
              onClick={handleLogout}
              className="bg-gray-100 hover:bg-gray-200 px-3 py-1.5 rounded text-gray-700"
            >
              Logout
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <Link to="/login" className="hover:text-primary">Employee Login</Link>
            <Link to="/admin/login" className="hover:text-primary">Admin Login</Link>
          </div>
        )}
      </div>
    </nav>
  );
}
