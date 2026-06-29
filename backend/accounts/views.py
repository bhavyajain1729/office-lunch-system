"""
Views for authentication & user profile.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    AdminLoginSerializer,
    EmployeeLoginSerializer,
    EmployeeRegisterSerializer,
    UserProfileSerializer,
)

User = get_user_model()


class EmployeeRegisterView(generics.CreateAPIView):
    """POST /api/auth/register/  — public employee self-registration."""

    queryset = User.objects.all()
    serializer_class = EmployeeRegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "detail": "Registration successful. You can now log in.",
                "user": UserProfileSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class EmployeeLoginView(TokenObtainPairView):
    """POST /api/auth/login/employee/"""

    serializer_class = EmployeeLoginSerializer
    permission_classes = [permissions.AllowAny]


class AdminLoginView(TokenObtainPairView):
    """POST /api/auth/login/admin/"""

    serializer_class = AdminLoginSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """
    POST /api/auth/logout/  — blacklists the supplied refresh token.
    Body: {"refresh": "<refresh_token>"}
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response({"detail": "Refresh token is required."}, status=400)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid or expired token."}, status=400)
        return Response({"detail": "Logged out successfully."}, status=200)


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/auth/profile/ — the currently authenticated user."""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
