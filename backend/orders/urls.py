"""
URL routes for the orders app.
Mounted at /api/orders/ in config/urls.py
"""

from django.urls import path

from .views import (
    ActivePaymentQRView,
    AdminDashboardView,
    AdminOrderDetailView,
    AdminOrderListView,
    AdminOrderStatusUpdateView,
    AdminPaymentQRUploadView,
    CheckoutView,
    MyOrderDetailView,
    MyOrderHistoryView,
    SubmitUTRView,
)

urlpatterns = [
    # Employee
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("<int:pk>/submit-utr/", SubmitUTRView.as_view(), name="submit-utr"),
    path("my-orders/", MyOrderHistoryView.as_view(), name="my-order-history"),
    path("my-orders/<int:pk>/", MyOrderDetailView.as_view(), name="my-order-detail"),
    path("payment-qr/", ActivePaymentQRView.as_view(), name="active-payment-qr"),

    # Admin
    path("admin/orders/", AdminOrderListView.as_view(), name="admin-order-list"),
    path("admin/orders/<int:pk>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),
    path("admin/orders/<int:pk>/status/", AdminOrderStatusUpdateView.as_view(), name="admin-order-status"),
    path("admin/payment-qr/", AdminPaymentQRUploadView.as_view(), name="admin-payment-qr"),
    path("admin/dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
]
