"""
Serializers for authentication & user profile endpoints.
Enhanced with session management and security.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserSession
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class EmployeeRegisterSerializer(serializers.ModelSerializer):
    """
    Public self-registration for employees. Role is always forced to
    EMPLOYEE here — admins cannot be created through this endpoint.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "employee_code",
            "department", "phone_number", "password", "password_confirm",
        ]

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password,
            role=User.Role.EMPLOYEE,
            **validated_data,
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile - excludes sensitive fields.
    Never expose password hashes or other sensitive data.
    """
    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "employee_code",
            "department", "phone_number", "role", "date_joined",
        ]
        read_only_fields = ["id", "role", "date_joined", "email"]


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for user session data."""
    class Meta:
        model = UserSession
        fields = [
            "id", "device_name", "device_fingerprint", "ip_address",
            "created_at", "last_activity", "expires_at", "status"
        ]
        read_only_fields = fields


class EnhancedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Base class for enhanced token serializers with session management.
    Creates UserSession records to track active sessions.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get("request")

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims to JWT
        token["role"] = user.role
        token["full_name"] = user.full_name
        token["email"] = user.email
        
        # Add session ID (jti - JWT ID claim)
        # This allows us to link JWT tokens to session records
        token["session_id"] = str(uuid.uuid4())
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Get device fingerprint from headers
        device_fingerprint = self._get_device_fingerprint()
        device_name = self._get_device_name()
        ip_address = self._get_client_ip()
        user_agent = self.request.META.get("HTTP_USER_AGENT", "") if self.request else ""
        
        # Get token JTI (unique identifier)
        refresh_token = RefreshToken.for_user(self.user)
        access_token = refresh_token.access_token
        
        # Create session record
        session = UserSession.objects.create(
            user=self.user,
            device_fingerprint=device_fingerprint,
            device_name=device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            access_token_jti=str(access_token.get("jti")),
            refresh_token_jti=str(refresh_token.get("jti")),
            expires_at=timezone.now() + timedelta(days=7),  # Match refresh token lifetime
        )
        
        # Add session info to response
        data["user"] = UserProfileSerializer(self.user).data
        data["session_id"] = str(session.id)
        
        return data

    def _get_device_fingerprint(self):
        """Generate device fingerprint from request headers."""
        if not self.request:
            return "unknown"
        
        user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        accept_language = self.request.META.get("HTTP_ACCEPT_LANGUAGE", "")
        
        # Combine for a simple fingerprint (in production, use more sophisticated methods)
        fingerprint = f"{user_agent}|{accept_language}"
        
        # Return hash of fingerprint
        import hashlib
        return hashlib.sha256(fingerprint.encode()).hexdigest()[:32]

    def _get_device_name(self):
        """Extract device name from user agent."""
        if not self.request:
            return "Unknown Device"
        
        user_agent = self.request.META.get("HTTP_USER_AGENT", "")
        
        # Simple device name extraction
        if "Chrome" in user_agent:
            device = "Chrome"
        elif "Firefox" in user_agent:
            device = "Firefox"
        elif "Safari" in user_agent:
            device = "Safari"
        elif "Edge" in user_agent:
            device = "Edge"
        else:
            device = "Unknown Browser"
        
        if "Windows" in user_agent:
            os = "Windows"
        elif "Macintosh" in user_agent:
            os = "macOS"
        elif "Linux" in user_agent:
            os = "Linux"
        elif "Android" in user_agent:
            os = "Android"
        elif "iPhone" in user_agent or "iPad" in user_agent:
            os = "iOS"
        else:
            os = "Unknown OS"
        
        return f"{device} on {os}"

    def _get_client_ip(self):
        """Get client IP address from request."""
        if not self.request:
            return None
        
        # Handle proxies
        x_forwarded_for = self.request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        
        return self.request.META.get("REMOTE_ADDR")


class EmployeeLoginSerializer(EnhancedTokenObtainPairSerializer):
    """
    Login restricted to employees. Admins must use the admin login
    endpoint, even though both share the same User table.
    """

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Role validation
        if self.user.role != User.Role.EMPLOYEE:
            raise serializers.ValidationError(
                "This login is for employees only. Admins should use the admin login."
            )
        
        return data


class AdminLoginSerializer(EnhancedTokenObtainPairSerializer):
    """Login restricted to admin/staff accounts."""

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Role validation
        if self.user.role != User.Role.ADMIN:
            raise serializers.ValidationError(
                "This login is for admins only."
            )
        
        return data


class SessionListSerializer(serializers.ModelSerializer):
    """Serializer for listing user sessions with privacy."""
    class Meta:
        model = UserSession
        fields = [
            "id", "device_name", "ip_address", "created_at", 
            "last_activity", "expires_at", "status"
        ]
        read_only_fields = fields
