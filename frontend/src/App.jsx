import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import ProtectedRoute from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";

import Home from "./pages/Home";
import EmployeeLogin from "./pages/EmployeeLogin";
import AdminLogin from "./pages/AdminLogin";
import Register from "./pages/Register";

import Menu from "./pages/employee/Menu";
import Checkout from "./pages/employee/Checkout";
import OrderHistory from "./pages/employee/OrderHistory";

import Dashboard from "./pages/admin/Dashboard";
import MenuManagement from "./pages/admin/MenuManagement";
import OrderManagement from "./pages/admin/OrderManagement";


<main className="min-h-screen bg-slate-50">
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/login" element={<EmployeeLogin />} />
    <Route path="/admin/login" element={<AdminLogin />} />
    <Route path="/register" element={<Register />} />

    <Route
      path="/menu"
      element={
        <ProtectedRoute role="EMPLOYEE">
          <Menu />
        </ProtectedRoute>
      }
    />

    <Route
      path="/checkout"
      element={
        <ProtectedRoute role="EMPLOYEE">
          <Checkout />
        </ProtectedRoute>
      }
    />

    <Route
      path="/orders"
      element={
        <ProtectedRoute role="EMPLOYEE">
          <OrderHistory />
        </ProtectedRoute>
      }
    />

    <Route
      path="/admin"
      element={
        <ProtectedRoute role="ADMIN">
          <Dashboard />
        </ProtectedRoute>
      }
    />

    <Route
      path="/admin/menu"
      element={
        <ProtectedRoute role="ADMIN">
          <MenuManagement />
        </ProtectedRoute>
      }
    />

    <Route
      path="/admin/orders"
      element={
        <ProtectedRoute role="ADMIN">
          <OrderManagement />
        </ProtectedRoute>
      }
    />

    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
</main>