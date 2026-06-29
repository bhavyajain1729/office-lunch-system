import api from "./client";

// --- Auth ---
export const registerEmployee = (data) => api.post("/auth/register/", data);
export const loginEmployee = (data) => api.post("/auth/login/employee/", data);
export const loginAdmin = (data) => api.post("/auth/login/admin/", data);
export const logout = (refresh) => api.post("/auth/logout/", { refresh });
export const getProfile = () => api.get("/auth/profile/");

// --- Menu (employee) ---
export const getTodayMenu = () => api.get("/menu/today/");

// --- Menu (admin) ---
export const getMenuItems = () => api.get("/menu/items/");
export const createMenuItem = (data) => api.post("/menu/items/", data);
export const updateMenuItem = (id, data) => api.patch(`/menu/items/${id}/`, data);
export const deleteMenuItem = (id) => api.delete(`/menu/items/${id}/`);

export const getDailyMenus = () => api.get("/menu/daily/");
export const createDailyMenu = (data) => api.post("/menu/daily/", data);
export const updateDailyMenu = (id, data) => api.patch(`/menu/daily/${id}/`, data);
export const getDailyMenuDetail = (id) => api.get(`/menu/daily/${id}/`);

// --- Orders (employee) ---
export const checkout = (data) => api.post("/orders/checkout/", data);
export const submitUTR = (orderId, utr_number) =>
  api.post(`/orders/${orderId}/submit-utr/`, { utr_number });
export const getMyOrders = () => api.get("/orders/my-orders/");
export const getActivePaymentQR = () => api.get("/orders/payment-qr/");

// --- Orders (admin) ---
export const getAdminOrders = (params) => api.get("/orders/admin/orders/", { params });
export const getAdminOrderDetail = (id) => api.get(`/orders/admin/orders/${id}/`);
export const updateOrderStatus = (id, data) =>
  api.patch(`/orders/admin/orders/${id}/status/`, data);
export const uploadPaymentQR = (formData) =>
  api.post("/orders/admin/payment-qr/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
export const getAdminDashboard = (date) =>
  api.get("/orders/admin/dashboard/", { params: date ? { date } : {} });
