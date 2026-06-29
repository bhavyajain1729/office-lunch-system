"""
Views for the orders app:
  - Employee: checkout (place order from cart), submit UTR, order history
  - Admin: list/manage all orders, dashboard stats, payment QR upload
"""

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminRole, IsEmployeeRole

from .models import Order, PaymentQRCode
from .serializers import (
    CheckoutSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    PaymentQRCodeSerializer,
    UTRSubmitSerializer,
)


# ---------------------------------------------------------------------------
# Employee: checkout & history
# ---------------------------------------------------------------------------
class CheckoutView(generics.CreateAPIView):
    """POST /api/orders/checkout/ — submit the cart and create an Order."""

    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployeeRole]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            {"detail": "Order placed. Please complete payment and submit your UTR number.",
             "order": OrderSerializer(order).data},
            status=status.HTTP_201_CREATED,
        )


class SubmitUTRView(APIView):
    """POST /api/orders/<id>/submit-utr/ — employee submits payment reference."""

    permission_classes = [permissions.IsAuthenticated, IsEmployeeRole]

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, employee=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=404)

        if order.status not in (Order.Status.PENDING_PAYMENT,):
            return Response(
                {"detail": f"Cannot submit UTR for an order in '{order.status}' status."},
                status=400,
            )

        serializer = UTRSubmitSerializer(data=request.data, context={"order": order})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(
            {"detail": "Payment reference submitted. Awaiting admin verification.",
             "order": OrderSerializer(order).data},
            status=200,
        )


class MyOrderHistoryView(generics.ListAPIView):
    """GET /api/orders/my-orders/ — the logged-in employee's order history."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployeeRole]
    filterset_fields = ["status", "order_date"]

    def get_queryset(self):
        return (
            Order.objects.filter(employee=self.request.user)
            .prefetch_related("items")
            .order_by("-created_at")
        )


class MyOrderDetailView(generics.RetrieveAPIView):
    """GET /api/orders/my-orders/<id>/ — single order detail for the owner."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployeeRole]

    def get_queryset(self):
        return Order.objects.filter(employee=self.request.user).prefetch_related("items")


class ActivePaymentQRView(APIView):
    """GET /api/orders/payment-qr/ — the currently active QR code, for checkout."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qr = PaymentQRCode.objects.filter(is_active=True).first()
        if not qr:
            return Response({"detail": "No payment QR code has been configured yet.", "qr": None})
        return Response({"detail": "", "qr": PaymentQRCodeSerializer(qr, context={"request": request}).data})


# ---------------------------------------------------------------------------
# Admin: order management
# ---------------------------------------------------------------------------
class AdminOrderListView(generics.ListAPIView):
    """GET /api/orders/admin/orders/ — all orders, filterable by date/status."""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    filterset_fields = ["status", "order_date", "employee"]

    def get_queryset(self):
        return Order.objects.select_related("employee").prefetch_related("items").order_by("-created_at")


class AdminOrderDetailView(generics.RetrieveAPIView):
    """GET /api/orders/admin/orders/<id>/"""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = Order.objects.select_related("employee").prefetch_related("items")


class AdminOrderStatusUpdateView(APIView):
    """
    PATCH /api/orders/admin/orders/<id>/status/
    Body: {"status": "CONFIRMED", "admin_remarks": "Verified on bank statement"}
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=404)

        serializer = OrderStatusUpdateSerializer(
            data=request.data, context={"order": order, "request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response({"detail": "Order status updated.", "order": OrderSerializer(order).data})


class AdminPaymentQRUploadView(generics.ListCreateAPIView):
    """
    GET  /api/orders/admin/payment-qr/  -> list all uploaded QR codes
    POST /api/orders/admin/payment-qr/  -> upload a new one (auto-deactivates others)
    """

    serializer_class = PaymentQRCodeSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    queryset = PaymentQRCode.objects.all()

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


# ---------------------------------------------------------------------------
# Admin: dashboard stats
# ---------------------------------------------------------------------------
class AdminDashboardView(APIView):
    """
    GET /api/orders/admin/dashboard/?date=YYYY-MM-DD
    Defaults to today. Returns summary stats for the admin dashboard.
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        date_str = request.query_params.get("date")
        target_date = timezone.localdate()
        if date_str:
            from datetime import date as date_cls
            try:
                target_date = date_cls.fromisoformat(date_str)
            except ValueError:
                return Response({"detail": "Invalid date format, expected YYYY-MM-DD."}, status=400)

        orders_today = Order.objects.filter(order_date=target_date)

        status_breakdown = {
            row["status"]: row["count"]
            for row in orders_today.values("status").annotate(count=Count("id"))
        }

        revenue_confirmed = orders_today.filter(
            status__in=[Order.Status.CONFIRMED, Order.Status.COMPLETED]
        ).aggregate(total=Sum("total_amount"))["total"] or 0

        pending_verification = orders_today.filter(status=Order.Status.PAYMENT_SUBMITTED).count()

        top_items = (
            orders_today.exclude(status__in=[Order.Status.CANCELLED, Order.Status.REJECTED])
            .values("items__item_name")
            .annotate(total_quantity=Sum("items__quantity"))
            .order_by("-total_quantity")[:5]
        )

        return Response({
            "date": target_date,
            "total_orders": orders_today.count(),
            "status_breakdown": status_breakdown,
            "pending_verification": pending_verification,
            "confirmed_revenue": revenue_confirmed,
            "top_items": [
                {"item_name": row["items__item_name"], "quantity": row["total_quantity"]}
                for row in top_items if row["items__item_name"]
            ],
        })
