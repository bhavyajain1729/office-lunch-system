"""
Views for authentication & user profile with enhanced security and session management.
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes

from .serializers import (
    AdminLoginSerializer,
    EmployeeLoginSerializer,
    EmployeeRegisterSerializer,
    UserProfileSerializer,
    SessionListSerializer,
)
from .models import UserSession
from .permissions import IsAdminRole, IsEmployeeRole

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
    """
    POST /api/auth/login/employee/
    
    Enhanced login with session tracking:
    - Creates UserSession record
    - Includes device fingerprinting
    - Returns session ID
    """

    serializer_class = EmployeeLoginSerializer
    permission_classes = [permissions.AllowAny]


class AdminLoginView(TokenObtainPairView):
    """
    POST /api/auth/login/admin/
    
    Enhanced admin login with session tracking:
    - Creates UserSession record
    - Includes device fingerprinting
    - Returns session ID
    """

    serializer_class = AdminLoginSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    
    Logout and revoke the session:
    - Invalidates refresh token (blacklist)
    - Marks session as revoked
    - Clears client-side tokens
    
    Body: {"refresh": "<refresh_token>", "session_id": "<session_uuid>"}
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        session_id = request.data.get("session_id")
        
        if not refresh:
            return Response(
                {"detail": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except TokenError:
            return Response(
                {"detail": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Mark session as revoked
        if session_id:
            try:
                session = UserSession.objects.get(id=session_id, user=request.user)
                session.revoke(reason="User logout")
            except UserSession.DoesNotExist:
                pass  # Session may have already been deleted
        
        return Response(
            {"detail": "Logged out successfully."},
            status=status.HTTP_200_OK
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/auth/profile/
    
    Retrieve or update the currently authenticated user's profile.
    Sensitive fields are read-only and not exposed.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        """
        Only allow updating non-sensitive fields.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Whitelist updatable fields
        allowed_fields = ['full_name', 'phone_number', 'department']
        
        for field in request.data:
            if field not in allowed_fields:
                return Response(
                    {"detail": f"Field '{field}' cannot be updated."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


class SessionListView(generics.ListAPIView):
    """
    GET /api/auth/sessions/
    
    List all active sessions for the current user.
    Allows users to:
    - See their active sessions across devices
    - Manage multi-device access
    - Identify unauthorized sessions
    """

    serializer_class = SessionListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return sessions for the authenticated user
        return UserSession.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class SessionTerminateView(APIView):
    """
    POST /api/auth/sessions/<session_id>/terminate/
    
    Terminate a specific session (revoke it).
    User can terminate their own sessions.
    Admins can terminate any session.
    
    Body: {"reason": "Device lost"} (optional)
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, session_id):
        try:
            session = UserSession.objects.get(id=session_id)
        except UserSession.DoesNotExist:
            return Response(
                {"detail": "Session not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Permission check: user can terminate their own sessions
        # Admins can terminate any session
        if session.user != request.user and request.user.role != User.Role.ADMIN:
            return Response(
                {"detail": "You cannot terminate other users' sessions."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reason = request.data.get("reason", "Manual termination")
        session.revoke(reason=reason)
        
        return Response(
            {
                "detail": "Session terminated successfully.",
                "session_id": str(session.id)
            },
            status=status.HTTP_200_OK
        )


class TerminateAllOtherSessionsView(APIView):
    """
    POST /api/auth/sessions/terminate-all-others/
    
    Terminate all sessions EXCEPT the current one.
    Useful for security: "Log out from all other devices"
    
    Body: {"current_session_id": "<session_uuid>"}
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        current_session_id = request.data.get("current_session_id")
        
        # Revoke all sessions except current one
        sessions_to_revoke = UserSession.objects.filter(
            user=request.user,
            status="active"
        )
        
        if current_session_id:
            sessions_to_revoke = sessions_to_revoke.exclude(id=current_session_id)
        
        count = 0
        for session in sessions_to_revoke:
            session.revoke(reason="User terminated all other sessions")
            count += 1
        
        return Response(
            {
                "detail": f"Terminated {count} other session(s).",
                "terminated_count": count
            },
            status=status.HTTP_200_OK
        )


class ValidateSessionView(APIView):
    """
    GET /api/auth/validate-session/
    
    Validate that the current session is still active.
    Used for periodic checks on the frontend.
    Refreshes last_activity timestamp.
    
    Returns: session details if valid, 401 if invalid
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Get session ID from request (frontend should send it)
        session_id = request.query_params.get("session_id")
        
        if not session_id:
            return Response(
                {"detail": "Session ID is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=request.user
            )
        except UserSession.DoesNotExist:
            return Response(
                {"detail": "Session not found or has been revoked."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not session.is_active:
            return Response(
                {"detail": "Session has expired or been revoked."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Update activity
        session.refresh_activity()
        
        return Response(
            {
                "valid": True,
                "session": SessionListSerializer(session).data,
                "user": UserProfileSerializer(request.user).data
            },
            status=status.HTTP_200_OK
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user_view(request):
    """
    GET /api/auth/me/
    
    Get current authenticated user's profile.
    Useful for initializing frontend after token refresh.
    """
    user = request.user
    return Response(
        {
            "user": UserProfileSerializer(user).data,
            "role": user.role,
            "is_admin": user.role == User.Role.ADMIN,
            "is_employee": user.role == User.Role.EMPLOYEE,
        },
        status=status.HTTP_200_OK
    )
