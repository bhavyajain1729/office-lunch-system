# JWT Security & Session Management - Implementation Guide

## Quick Start

This guide walks through the complete JWT token security and session management implementation.

## What's Changed

### Backend Changes

#### 1. New UserSession Model
- **File**: `backend/accounts/models.py`
- **Tracks**: Device fingerprints, IP addresses, session status
- **Features**: Multi-device support, session revocation, activity tracking

#### 2. Enhanced Serializers
- **File**: `backend/accounts/serializers.py`
- **New Base Class**: `EnhancedTokenObtainPairSerializer`
- **Features**: Automatic session creation, device detection, token metadata

#### 3. Enhanced Views
- **File**: `backend/accounts/views.py`
- **New Endpoints**:
  - `GET /api/auth/sessions/` - List active sessions
  - `POST /api/auth/sessions/<id>/terminate/` - Terminate specific session
  - `POST /api/auth/sessions/terminate-all-others/` - Logout from all other devices
  - `GET /api/auth/validate-session/` - Validate current session
  - `GET /api/auth/me/` - Get current user

#### 4. New Migration
- **File**: `backend/accounts/migrations/0002_usersession.py`
- **Creates**: `user_sessions` table with indexes

### Frontend Changes

#### 1. Enhanced AuthContext
- **File**: `frontend/src/context/AuthContext.jsx`
- **Features**:
  - Automatic logout on tab close (`beforeunload`)
  - Periodic session validation (every 5 minutes)
  - Session ID tracking
  - Visibility change detection

#### 2. Updated API Endpoints
- **File**: `frontend/src/api/endpoints.js`
- **New Functions**:
  - `getSessions()` - List active sessions
  - `terminateSession(sessionId, reason)` - Terminate session
  - `terminateAllOtherSessions(currentSessionId)` - Log out other devices
  - `validateSession(sessionId)` - Check session validity

#### 3. Session Management UI
- **File**: `frontend/src/pages/admin/SessionManagement.jsx`
- **Features**: View active sessions, terminate devices, logout all others

## Installation Steps

### Step 1: Apply Database Migration

```bash
# Navigate to backend
cd backend

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Verify migration
python manage.py showmigrations accounts
```

### Step 2: Update Backend Dependencies

No additional dependencies needed - uses existing packages:
- `djangorestframework-simplejwt` (already installed)
- `django.contrib.auth` (built-in)

### Step 3: Frontend Setup

No additional npm packages needed - uses existing:
- `react` (already installed)
- `axios` (via api/client.js)

### Step 4: Test the Implementation

#### Test Backend

```bash
# Start backend
cd backend
python manage.py runserver

# In another terminal, test endpoints
# 1. Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@company.com",
    "full_name": "Test User",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'

# 2. Login (save tokens)
RESPONSE=$(curl -X POST http://localhost:8000/api/auth/login/employee/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@company.com",
    "password": "SecurePass123!"
  }')

# Extract tokens from response
# ACCESS_TOKEN="..." 
# REFRESH_TOKEN="..."
# SESSION_ID="..."

# 3. Get current user
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 4. List sessions
curl http://localhost:8000/api/auth/sessions/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 5. Validate session
curl "http://localhost:8000/api/auth/validate-session/?session_id=$SESSION_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# 6. Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh\": \"$REFRESH_TOKEN\",
    \"session_id\": \"$SESSION_ID\"
  }"
```

#### Test Frontend

```bash
# Start frontend
cd frontend
npm run dev

# 1. Open http://localhost:5173
# 2. Register a new employee account
# 3. Login - notice session tracking starts
# 4. Check browser console for session validation
# 5. Open DevTools -> Storage -> Local Storage
#    - Verify access_token, refresh_token, session_id saved
# 6. Close one tab - automatic logout triggers
# 7. Verify tokens cleared from localStorage
```

## Security Features Explained

### 1. Automatic Logout on Tab Close

**How it works:**
```javascript
// frontend/src/context/AuthContext.jsx (line ~140)
window.addEventListener("beforeunload", async (e) => {
  navigator.sendBeacon("/api/auth/logout/", logoutData);
  clearAuthData();
});
```

**Why `sendBeacon`?**
- Works even if browser is closing
- Browser guarantees delivery
- Doesn't block page unload
- More reliable than fetch in unload handlers

### 2. Role-Based Access Control

**Employees can only see:**
- Today's menu items
- Their own orders
- Their own profile

**Admins can see:**
- Menu management
- Order management dashboard
- All orders across all employees
- Payment verification

**How it's enforced:**
```python
# backend/accounts/permissions.py
class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "ADMIN"

# In views
class OrderAdminView(generics.ListAPIView):
    permission_classes = [IsAdminRole]  # Only admins
```

### 3. Session Tracking

**Every login creates a session record:**
```python
# backend/accounts/models.py
UserSession.objects.create(
    user=user,
    device_fingerprint=hash(user_agent + language),
    device_name="Chrome on Windows",
    ip_address="192.168.1.100",
    access_token_jti="unique-jwt-id",
    refresh_token_jti="unique-jwt-id",
    expires_at=now + 7_days
)
```

**Benefits:**
- Multi-device login tracking
- Device recognition
- Session revocation
- Activity monitoring

### 4. Periodic Session Validation

**Frontend validates session every 5 minutes:**
```javascript
// frontend/src/context/AuthContext.jsx (line ~160)
setInterval(() => {
  validateCurrentSession();  // Calls /api/auth/validate-session/
}, 5 * 60 * 1000);  // 5 minutes
```

**What it checks:**
- Session still exists in database
- Session not revoked
- Session hasn't expired
- User still active

### 5. Password Security

**Validation includes:**
- Minimum 8 characters
- Cannot match email/name/common passwords
- Must be complex enough
- Hashed with PBKDF2 + salt

**Never exposed:**
- Password never returned in API responses
- Never logged
- Never stored in localStorage
- Only transmitted over HTTPS

## Usage Examples

### Example 1: Protected Employee Route

```javascript
// frontend/src/App.jsx
import ProtectedRoute from "./components/ProtectedRoute";
import Menu from "./pages/employee/Menu";

<Routes>
  <Route path="/menu" element={
    <ProtectedRoute roles={["EMPLOYEE"]}>
      <Menu />
    </ProtectedRoute>
  } />
</Routes>
```

### Example 2: Login with Session Tracking

```javascript
// frontend/src/pages/EmployeeLogin.jsx
async function handleLogin(email, password) {
  const { loginAsEmployee } = useAuth();
  
  try {
    const user = await loginAsEmployee(email, password);
    // User logged in
    // Session created on backend
    // Tokens saved in localStorage
    // Automatic logout on tab close enabled
    // Session validation started
    navigate("/menu");
  } catch (error) {
    setError(error.response?.data?.detail);
  }
}
```

### Example 3: View Active Sessions

```javascript
// frontend/src/pages/admin/SessionManagement.jsx
import { getSessions, terminateSession } from "../../api/endpoints";

useEffect(() => {
  getSessions().then(response => {
    setSessions(response.data);  // List of all user sessions
  });
}, []);

function handleTerminate(sessionId) {
  terminateSession(sessionId, "User requested termination")
    .then(() => {
      // Session terminated - device logged out
      fetchSessions();  // Refresh list
    });
}
```

### Example 4: Logout All Other Devices

```javascript
// frontend/src/pages/Settings.jsx
import { terminateAllOtherSessions } from "../../api/endpoints";

async function handleLogoutOtherDevices() {
  const result = await terminateAllOtherSessions(sessionId);
  console.log(`Logged out ${result.terminated_count} devices`);
  // Only current device remains logged in
}
```

## Database Schema

### UserSession Table

```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL,
    device_fingerprint VARCHAR(255) NOT NULL,
    device_name VARCHAR(200),
    ip_address INET,
    user_agent TEXT,
    access_token_jti VARCHAR(255) UNIQUE NOT NULL,
    refresh_token_jti VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP,
    last_activity TIMESTAMP,
    expires_at TIMESTAMP,
    status VARCHAR(20),  -- 'active', 'revoked', 'expired'
    logout_reason VARCHAR(200),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for performance
CREATE INDEX idx_sessions_user_status ON user_sessions(user_id, status);
CREATE INDEX idx_sessions_access_jti ON user_sessions(access_token_jti);
CREATE INDEX idx_sessions_refresh_jti ON user_sessions(refresh_token_jti);
```

## API Response Examples

### Login Response
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "user": {
    "id": 1,
    "email": "user@company.com",
    "full_name": "John Doe",
    "role": "EMPLOYEE",
    "employee_code": "EMP001",
    "department": "Engineering",
    "phone_number": "+1234567890",
    "date_joined": "2024-01-01T10:00:00Z"
  }
}
```

### Session List Response
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "device_name": "Chrome on Windows",
    "ip_address": "192.168.1.100",
    "created_at": "2024-01-15T10:30:00Z",
    "last_activity": "2024-01-15T10:45:00Z",
    "expires_at": "2024-01-22T10:30:00Z",
    "status": "active"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "device_name": "Safari on macOS",
    "ip_address": "192.168.1.101",
    "created_at": "2024-01-14T15:20:00Z",
    "last_activity": "2024-01-14T16:00:00Z",
    "expires_at": "2024-01-21T15:20:00Z",
    "status": "active"
  }
]
```

## Troubleshooting

### Issue: Migration fails
**Solution:**
```bash
python manage.py makemigrations --dry-run  # See what will happen
python manage.py makemigrations
python manage.py sqlmigrate accounts 0002  # See SQL
python manage.py migrate
```

### Issue: Session not persisting after page refresh
**Check:**
1. Open DevTools -> Application -> Local Storage
2. Verify `access_token`, `refresh_token`, `session_id` exist
3. Check browser console for errors
4. Verify AuthContext is wrapping entire app

### Issue: Logout not working
**Check:**
1. Backend receives logout request: `curl -v ...` to see response
2. Verify refresh token in request body
3. Check database: `SELECT * FROM user_sessions WHERE status='revoked';`
4. Verify localStorage is actually cleared

### Issue: Automatic logout on tab close not working
**Check:**
1. Browser supports `beforeunload` event
2. Open Network tab while closing tab - should see logout request
3. Check browser console for errors
4. Try different browser (some have privacy restrictions)

## Next Steps

### For Development
1. ✅ Add 2FA/Multi-factor authentication
2. ✅ Add IP whitelisting
3. ✅ Add suspicious activity detection
4. ✅ Implement rate limiting on login
5. ✅ Add detailed audit logging

### For Testing
```bash
# Run Django tests
python manage.py test accounts

# Test specific test case
python manage.py test accounts.tests.AuthenticationTests.test_login_creates_session
```

### For Production
1. Set `DEBUG=False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Enable HTTPS/SSL
4. Set strong `SECRET_KEY`
5. Configure logging
6. Set up database backups
7. Review token lifetimes
8. Enable rate limiting

## Summary

This implementation provides:
- ✅ **Secure JWT tokens** with rotation and blacklisting
- ✅ **Session tracking** across multiple devices
- ✅ **Automatic logout** on tab close
- ✅ **Role-based access control** (EMPLOYEE vs ADMIN)
- ✅ **Periodic validation** to detect revoked sessions
- ✅ **Password security** with hashing and validation
- ✅ **Data privacy** - sensitive fields protected
- ✅ **Device fingerprinting** - detect login locations
- ✅ **Activity tracking** - monitor session usage

Users can no longer:
- ❌ See other users' passwords
- ❌ Access other users' data
- ❌ Stay logged in when they close the browser
- ❌ Use revoked tokens
- ❌ Access admin features without admin role
- ❌ Share sessions across devices without detection
