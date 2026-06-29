"""
Serializers for authentication & user profile endpoints.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "employee_code",
            "department", "phone_number", "role", "date_joined",
        ]
        read_only_fields = ["id", "role", "date_joined"]


class EmployeeLoginSerializer(TokenObtainPairSerializer):
    """
    Login restricted to employees. Admins must use the admin login
    endpoint, even though both share the same User table.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["full_name"] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role != User.Role.EMPLOYEE:
            raise serializers.ValidationError(
                "This login is for employees only. Admins should use the admin login."
            )
        data["user"] = UserProfileSerializer(self.user).data
        return data


class AdminLoginSerializer(TokenObtainPairSerializer):
    """Login restricted to admin/staff accounts."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["full_name"] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role != User.Role.ADMIN:
            raise serializers.ValidationError(
                "This login is for admins only."
            )
        data["user"] = UserProfileSerializer(self.user).data
        return data
