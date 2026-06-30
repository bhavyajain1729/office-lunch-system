"""
Custom User model for the Office Lunch Ordering System.

Employees self-register through the public API. Admins (canteen /
HR staff who manage the menu and orders) are created via the Django
admin or `manage.py promote_admin` and are never created through the public registration endpoint.
"""

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
import uuid
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager since we authenticate by email, not username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.EMPLOYEE)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Application user.

    role=EMPLOYEE -> can browse menu, place orders, view own order history.
    role=ADMIN    -> can manage menu items, daily menus, and all orders.
    """

    class Role(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "Employee"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    employee_code = models.CharField(
        max_length=30, unique=True, null=True, blank=True,
        help_text="Optional internal employee/staff ID.",
    )
    department = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.EMPLOYEE)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Django admin site access
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        db_table = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.full_name} <{self.email}> ({self.role})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN


class UserSession(models.Model):
    """
    Tracks active user sessions with JWT tokens.
    Enables multi-device login, session management, and device fingerprinting.
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("revoked", "Revoked"),
        ("expired", "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    
    # Session metadata
    device_fingerprint = models.CharField(max_length=255, help_text="Browser/device identifier")
    device_name = models.CharField(max_length=200, blank=True, help_text="e.g., 'Chrome on Windows'")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Token metadata
    access_token_jti = models.CharField(max_length=255, unique=True, help_text="JWT ID for access token")
    refresh_token_jti = models.CharField(max_length=255, unique=True, help_text="JWT ID for refresh token")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="When the refresh token expires")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    logout_reason = models.CharField(max_length=200, blank=True, help_text="Reason for logout/revocation")

    class Meta:
        db_table = "user_sessions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["access_token_jti"]),
            models.Index(fields=["refresh_token_jti"]),
        ]

    def __str__(self):
        return f"Session {self.id} for {self.user.email}"

    @property
    def is_active(self):
        return self.status == "active" and timezone.now() < self.expires_at

    def revoke(self, reason="Manual logout"):
        """Revoke this session."""
        self.status = "revoked"
        self.logout_reason = reason
        self.save()

    def refresh_activity(self):
        """Update last activity timestamp."""
        self.last_activity = timezone.now()
        self.save(update_fields=["last_activity"])
