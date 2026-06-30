# Security Implementation Guide

## Overview

This document outlines the comprehensive JWT token security and session management implementation for the Office Lunch Ordering System.

## Features Implemented

### 1. **JWT Token Security**

#### Access & Refresh Tokens
- **Access Token**: Short-lived (30 minutes) for API requests
- **Refresh Token**: Long-lived (7 days) for obtaining new access tokens
- **Token Rotation**: New tokens issued on refresh to prevent token reuse
- **Blacklisting**: Revoked tokens are blacklisted and invalid

#### Token Claims
Each JWT token includes:
```json
{
  "user_id": 123,
  "email": "user@company.com",
  "role": "EMPLOYEE",
  "full_name": "John Doe",
  "session_id": "unique-session-uuid",
  "jti": "unique-token-id"
}
```

### 2. **Session Management**

#### UserSession Model
Tracks active sessions with:
- **Device Fingerprinting**: Identifies browser/device combinations
- **IP Address**: Logs client IP for security auditing
- **Device Name**: Human-readable device info (e.g., "Chrome on Windows")
- **Session Status**: Active, Revoked, or Expired
- **Timestamps**: Creation, last activity, expiration

```
UserSession Fields:
├── id (UUID primary key)
├── user (ForeignKey to User)
├── device_fingerprint (SHA256 hash)
├── device_name (e.g., "Chrome on Windows")
├── ip_address (tracked for security)
├── user_agent (raw browser string)
├── access_token_jti (unique JWT ID)
├── refresh_token_jti (unique JWT ID)
├── created_at (session creation)
├── last_activity (last request time)
├── expires_at (refresh token expiry)
└── status (active/revoked/expired)
```

### 3. **Automatic Logout on Tab Close**

#### Frontend Implementation
When a user closes a tab/window:
1. `beforeunload` event triggers
2. `navigator.sendBeacon()` sends logout request (reliable even on unload)
3. Refresh token is blacklisted
4. Session is marked as revoked
5. Local storage is cleared

```javascript
// Example: beforeunload handler
window.addEventListener("beforeunload", async (e) => {
  const sessionId = localStorage.getItem("session_id");
  const refresh = localStorage.getItem("refresh_token");
  
  if (sessionId && refresh) {
    navigator.sendBeacon("/api/auth/logout/", JSON.stringify({
      refresh,
      session_id: sessionId
    }));
  }
});
```

### 4. **Role-Based Access Control**

#### User Roles
- **EMPLOYEE**: Can browse menu, place orders, view own history
- **ADMIN**: Can manage menu, process orders, view all orders

#### Permission Classes
```python
# backend/accounts/permissions.py
IsEmployeeRole  # Only employees
IsAdminRole     # Only admins
```

#### Access Control Implementation
- JWT token includes `role` claim
- Backend validates role on every request
- Endpoints check role-based permissions
- Frontend protects routes based on role

### 5. **Session Validation**

#### Periodic Validation
- Frontend validates session every 5 minutes
- Checks if session still active and not revoked
- Updates `last_activity` timestamp on validation
- Automatically logs out if session invalid

#### Validation Endpoint
```
GET /api/auth/validate-session/?session_id=<uuid>
Response:
{
  "valid": true,
  "session": { session details },
  "user": { user profile }
}
```

### 6. **Password & Data Security**

#### Password Security
- Minimum 8 characters
- Must not be similar to email/name
- Cannot be common passwords
- Must include numbers/special chars
- Stored using Django's PBKDF2 hashing

#### Data Privacy
- User profile endpoint never exposes password hashes
- Sensitive fields marked as `read_only`
- Password returned as `write_only` (only on input)
- User data filtered before API responses

#### Field Protection
```python
# UserProfileSerializer - never includes:
- password
- password_hash
- is_superuser
- is_staff

# Only includes:
- id
- email
- full_name
- employee_code
- department
- phone_number
- role
- date_joined
```

## API Endpoints

### Authentication

#### 1. Register Employee
```
POST /api/auth/register/
Body: {
  "email": "user@company.com",
  "full_name": "John Doe",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
Response: 201 Created
{
  "detail": "Registration successful",
  "user": { user profile }
}
```

#### 2. Employee Login
```
POST /api/auth/login/employee/
Body: {
  "email": "user@company.com",
  "password": "SecurePass123!"
}
Response: 200 OK
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user": { user profile }
}
```

#### 3. Admin Login
```
POST /api/auth/login/admin/
Body: {
  "email": "admin@company.com",
  "password": "AdminPass123!"
}
Response: 200 OK
{
  "access": "...",
  "refresh": "...",
  "session_id": "...",
  "user": { admin profile with role: "ADMIN" }
}
```

#### 4. Logout (Revoke Session)
```
POST /api/auth/logout/
Headers: Authorization: Bearer <access_token>
Body: {
  "refresh": "<refresh_token>",
  "session_id": "<session_uuid>"
}
Response: 200 OK
{
  "detail": "Logged out successfully"
}
```

#### 5. Get Current User
```
GET /api/auth/me/
Headers: Authorization: Bearer <access_token>
Response: 200 OK
{
  "user": { user profile },
  "role": "EMPLOYEE",
  "is_admin": false,
  "is_employee": true
}
```

### Session Management

#### 1. List Active Sessions
```
GET /api/auth/sessions/
Headers: Authorization: Bearer <access_token>
Response: 200 OK
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "device_name": "Chrome on Windows",
    "ip_address": "192.168.1.100",
    "created_at": "2024-01-15T10:30:00Z",
    "last_activity": "2024-01-15T10:45:00Z",
    "expires_at": "2024-01-22T10:30:00Z",
    "status": "active"
  }
]
```

#### 2. Terminate Specific Session
```
POST /api/auth/sessions/<session_id>/terminate/
Headers: Authorization: Bearer <access_token>
Body: {
  "reason": "Device lost"
}
Response: 200 OK
{
  "detail": "Session terminated successfully",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 3. Terminate All Other Sessions
```
POST /api/auth/sessions/terminate-all-others/
Headers: Authorization: Bearer <access_token>
Body: {
  "current_session_id": "<session_uuid>"
}
Response: 200 OK
{
  "detail": "Terminated 3 other session(s)",
  "terminated_count": 3
}
```

#### 4. Validate Session
```
GET /api/auth/validate-session/?session_id=<uuid>
Headers: Authorization: Bearer <access_token>
Response: 200 OK
{
  "valid": true,
  "session": { session details },
  "user": { user profile }
}
```

## Frontend Implementation

### AuthContext Hooks

#### useAuth() Hook
```javascript
const {
  user,              // Current user object
  sessionId,         // Current session UUID
  isAuthenticated,   // Boolean
  isAdmin,           // Boolean
  isEmployee,        // Boolean
  loading,           // Boolean
  isSessionValid,    // Boolean
  loginAsEmployee,   // Function
  loginAsAdmin,      // Function
  logout,            // Function
  validateSession,   // Function
  clearAuth          // Function
} = useAuth();
```

### Login Flow

```javascript
import { useAuth } from "../context/AuthContext";

function LoginPage() {
  const { loginAsEmployee } = useAuth();
  
  async function handleLogin(email, password) {
    try {
      const user = await loginAsEmployee(email, password);
      // Tokens saved automatically
      // Session tracked
      // Automatic logout on close enabled
      navigate("/menu");
    } catch (error) {
      console.error(error);
    }
  }
}
```

### Protected Routes

```javascript
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function AdminRoute({ children }) {
  const { isAdmin, isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  if (!isAdmin) {
    return <Navigate to="/menu" />;
  }
  
  return children;
}

// Usage
<Route path="/admin" element={
  <AdminRoute>
    <AdminDashboard />
  </AdminRoute>
} />
```

### Logout on Tab Close

Implemented automatically in AuthContext:
- No additional code needed
- Works across all tabs
- Uses `navigator.sendBeacon()` for reliability
- Falls back to localStorage clearing

## Security Best Practices

### Backend

1. **Always Use HTTPS** in production
2. **CORS Configuration**: Only allow frontend domains
3. **CSRF Protection**: Enabled by default
4. **SQL Injection**: Using Django ORM (parameterized queries)
5. **Password Hashing**: PBKDF2 with salt
6. **Rate Limiting**: Implement on login endpoints (future)
7. **Logging**: Audit login/logout events
8. **Secrets**: Use environment variables

### Frontend

1. **Token Storage**: localStorage (cleared on logout)
2. **XSS Protection**: React escapes by default
3. **Secure Headers**: Set in CORS config
4. **Input Validation**: Validate all forms
5. **HTTPS Only**: Force HTTPS in production
6. **Session Validation**: Periodic checks (5 min)
7. **Automatic Cleanup**: Clear data on tab close

## Configuration

### Backend (settings.py)

```python
# JWT Configuration
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),    # 30 minutes
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),       # 7 days
    "ROTATE_REFRESH_TOKENS": True,                     # Rotate on refresh
    "BLACKLIST_AFTER_ROTATION": True,                  # Blacklist old tokens
    "UPDATE_LAST_LOGIN": True,                         # Track last login
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://yourfrontend.com",
]

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", 
     "OPTIONS": {"min_length": 8}},
    # ... more validators
]
```

### Frontend (.env)

```
VITE_API_URL=http://localhost:8000/api
VITE_SESSION_CHECK_INTERVAL=300000  # 5 minutes in ms
```

## Testing Security

### Test Login/Logout
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@company.com",
    "full_name": "Test User",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/employee/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@company.com",
    "password": "TestPass123!"
  }'

# Note: Save access_token, refresh_token, and session_id

# Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<refresh_token>",
    "session_id": "<session_id>"
  }'
```

### Test Session Management
```bash
# List sessions
curl http://localhost:8000/api/auth/sessions/ \
  -H "Authorization: Bearer <access_token>"

# Validate session
curl "http://localhost:8000/api/auth/validate-session/?session_id=<session_id>" \
  -H "Authorization: Bearer <access_token>"

# Terminate session
curl -X POST http://localhost:8000/api/auth/sessions/<session_id>/terminate/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Testing"}'

# Terminate all others
curl -X POST http://localhost:8000/api/auth/sessions/terminate-all-others/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"current_session_id": "<session_id>"}'
```

## Security Checklist

### Before Production

- [ ] Change Django SECRET_KEY (environment variable)
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for production domain
- [ ] Enable CSRF protection
- [ ] Review password validators
- [ ] Set up rate limiting on login
- [ ] Enable logging for security events
- [ ] Database backups configured
- [ ] Review token lifetimes
- [ ] Test session management
- [ ] Document incident response procedures
- [ ] Enable monitoring/alerting
- [ ] Test token refresh flow
- [ ] Verify automatic logout on tab close
- [ ] Test with multiple devices
- [ ] Review role-based access control

## Troubleshooting

### Session Doesn't Persist After Refresh
- Check that `session_id` is saved in localStorage
- Verify `access_token` and `refresh_token` are saved
- Check browser console for errors

### Logout Not Working
- Verify refresh token is being sent
- Check that backend receives logout request
- Verify session_id is correct
- Check database for session status

### Automatic Logout on Tab Close Not Working
- Check browser supports `beforeunload` event
- Verify `navigator.sendBeacon()` is supported
- Check network tab for logout request
- Verify localStorage is being cleared

### Sessions Keep Expiring
- Check token expiration times
- Verify periodic validation is running
- Check `last_activity` timestamps
- Review session validation interval

## Future Enhancements

1. **2FA/MFA**: Two-factor authentication
2. **OAuth2**: Social login integration
3. **IP Whitelisting**: Restrict access by IP
4. **Geo-blocking**: Detect suspicious locations
5. **Device Trust**: Remember trusted devices
6. **Biometric Auth**: Fingerprint/face recognition
7. **Security Questions**: Additional verification
8. **Token Encryption**: Encrypt tokens at rest
9. **Audit Logging**: Detailed security audit trail
10. **Anomaly Detection**: ML-based suspicious activity detection

## Support

For security issues or questions:
- Email: security@yourcompany.com
- Do not create public GitHub issues for security vulnerabilities
- Use responsible disclosure practices

## References

- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [RFC 7234 - HTTP Caching](https://tools.ietf.org/html/rfc7234)
