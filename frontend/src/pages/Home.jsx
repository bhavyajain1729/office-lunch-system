import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Home() {
  const { isAuthenticated, isAdmin } = useAuth();

  if (isAuthenticated) {
    return (
      <div className="max-w-2xl mx-auto mt-16 text-center">
        <h1 className="text-2xl font-bold mb-4">Welcome back!</h1>
        <Link
          to={isAdmin ? "/admin" : "/menu"}
          className="inline-block bg-primary text-white px-5 py-2 rounded hover:bg-primary-dark"
        >
          {isAdmin ? "Go to Dashboard" : "View Today's Menu"}
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto mt-16 text-center">
      <h1 className="text-3xl font-bold mb-2">🍱 Office Lunch Ordering</h1>
      <p className="text-gray-600 mb-8">
        Order your daily office lunch, pay by UPI QR, and track your orders — all in one place.
      </p>
      <div className="flex justify-center gap-4">
        <Link
          to="/login"
          className="bg-primary text-white px-5 py-2 rounded hover:bg-primary-dark"
        >
          Employee Login
        </Link>
        <Link
          to="/register"
          className="bg-white border border-gray-300 px-5 py-2 rounded hover:bg-gray-50"
        >
          Employee Sign Up
        </Link>
        <Link
          to="/admin/login"
          className="bg-gray-800 text-white px-5 py-2 rounded hover:bg-gray-700"
        >
          Admin Login
        </Link>
      </div>
    </div>
  );
}
