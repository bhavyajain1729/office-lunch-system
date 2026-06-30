# JWT Security Implementation - Quick Start Guide

## 🎯 What Was Done

Your Office Lunch System now has enterprise-grade JWT token security with automatic logout on tab close and role-based session management.

### Problems Solved ✅

| Problem | Solution |
|---------|----------|
| Users stay logged in after closing browser | Automatic logout via `beforeunload` event + `navigator.sendBeacon()` |
| No password/data security | Encrypted passwords (PBKDF2), filtered API responses, protected fields |
| No session tracking | `UserSession` model tracks device fingerprints, IPs, activity |
| No role-based separation | JWT claims + permission classes enforce EMPLOYEE vs ADMIN roles |
| No token security | Token rotation, blacklisting, expiration, session binding |

---

## 🚀 Getting Started (5 Minutes)

### 1. Apply Database Migration
```bash
cd backend
python manage.py migrate
```

### 2. Create Admin Account (if needed)
```bash
python manage.py promote_admin \
  --email admin@company.com \
  --create \
  --password "AdminPass123" \
  --full-name "Admin User"
```

### 3. Start Backend
```bash
python manage.py runserver
# Backend runs at http://localhost:8000
```

### 4. Start Frontend (New Terminal)
```bash
cd frontend
npm run dev
# Frontend runs at http://localhost:5173
```

### 5. Test in Browser
- Go to http://localhost:5173
- Register a new employee account
- Login
- **Close the browser tab** → Automatic logout happens!
- Open DevTools → Application → Local Storage → Tokens should be cleared

---

## 🔐 Key Features You Now Have

### Feature 1: Automatic Logout on Tab Close ✅
When user closes tab/browser:
```
1. beforeunload event fires
2. navigator.sendBeacon() sends logout to backend
3. Refresh token is blacklisted
4. Session marked as revoked
5. localStorage cleared
→ User is logged out everywhere
```

### Feature 2: Secure Session Tracking ✅
Every login creates a session record with:
- Device name (e.g., "Chrome on Windows")
- IP address (for location tracking)
- Device fingerprint (browser/OS hash)
- Token JTI (unique identifier)
- Activity timestamps

### Feature 3: Role-Based Access Control ✅
**Employees can:**
- Browse today's menu
- Place orders
- View own order history

**Admins can:**
- Manage menu
- View all orders
- Process payments
- Access admin dashboard

### Feature 4: Periodic Session Validation ✅
Frontend validates session every 5 minutes:
- Is session still active?
- Was it revoked?
- Did it expire?
→ Auto-logout if invalid

### Feature 5: Multi-Device Login ✅
Users can login from multiple devices:
- Each login creates separate session
- Devices tracked independently
- Can terminate specific device
- Can logout from all others

---

## 📱 New Features for Users

### For Employees
1. **Sessions Page** (Admin area):
   - View all active login sessions
   - See device names and IP addresses
   - See login times and last activity
   - Terminate specific sessions

2. **Security Features**:
   - Automatic logout when closing browser
   - Session validation every 5 minutes
   - Password hashing (cannot be stolen)
   - Role enforcement (can't access admin features)

### For Admins
1. **Session Management**:
   - View all user sessions
   - Terminate unauthorized sessions
   - Force logout from all other devices
   - Monitor login activity

2. **Security**:
   - Audit trail of logins/logouts
   - Device fingerprinting
   - IP address tracking
   - Session status (active/revoked/expired)

---

## 🔌 New API Endpoints

### Session Management
```
GET    /api/auth/sessions/
  → List all active sessions for current user

POST   /api/auth/sessions/<id>/terminate/
  → Logout from specific device

POST   /api/auth/sessions/terminate-all-others/
  → Logout from all devices except current

GET    /api/auth/validate-session/?session_id=<uuid>
  → Check if session is still valid

GET    /api/auth/me/
  → Get current user info

POST   /api/auth/logout/
  → Logout (now includes session revocation)
```

---

## 📁 Files Changed

### Backend
```
backend/accounts/
├── models.py              ← Added UserSession model
├── serializers.py         ← Enhanced with device detection
├── views.py               ← 5 new security endpoints
├── urls.py                ← Route registration
└── migrations/
    └── 0002_usersession.py ← NEW: Database migration
```

### Frontend
```
frontend/src/
├── context/
│   └── AuthContext.jsx    ← Auto-logout, session validation
├── api/
│   └── endpoints.js       ← 5 new session endpoints
└── pages/admin/
    └── SessionManagement.jsx ← NEW: Session management UI
```

### Documentation
```
├── SECURITY.md                          ← Complete security guide
├── IMPLEMENTATION_GUIDE.md              ← Setup & testing guide
└── SECURITY_IMPLEMENTATION_SUMMARY.md   ← Quick reference
```

---

## ✅ Testing Checklist

### Quick Tests (5 minutes)
- [ ] Register new employee account
- [ ] Login successfully
- [ ] Check localStorage has tokens (DevTools > Application)
- [ ] Close browser tab
- [ ] Check localStorage is empty (tokens cleared)
- [ ] Login again with different browser

### Security Tests (10 minutes)
- [ ] Try to access `/admin` as employee → Redirected
- [ ] Login as admin → Can access admin features
- [ ] Open session management page
- [ ] See multiple sessions from different logins
- [ ] Terminate a session → That device logs out
- [ ] "Logout all others" → Only current device remains

### Advanced Tests (15 minutes)
- [ ] Login on 2 different browsers
- [ ] Go to Admin > Sessions > See both
- [ ] Terminate browser 1 session from browser 2
- [ ] Browser 1 auto-logs out
- [ ] Browser 2 still logged in
- [ ] Close browser 2 → Auto-logout triggers

---

## 🔒 Security Features

### Implemented ✅
- JWT tokens (30 min access, 7 day refresh)
- Token rotation on refresh
- Token blacklisting on logout
- Automatic logout on tab close
- Session tracking & device fingerprinting
- Role-based access control
- Password hashing (PBKDF2)
- Periodic session validation
- IP address logging
- User data filtering

### Ready for Production ⚠️
- HTTPS/SSL (set up on your server)
- Rate limiting (add to /api/auth/login/)
- Audit logging (log to database)
- 2FA/MFA (future enhancement)
- Session inactivity timeout (future)

---

## 🧪 Test With curl

### 1. Register
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@company.com",
    "full_name": "Test User",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

### 2. Login (copy tokens)
```bash
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login/employee/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@company.com",
    "password": "SecurePass123!"
  }')

# Extract from response:
# ACCESS_TOKEN=...
# REFRESH_TOKEN=...
# SESSION_ID=...
```

### 3. Get Current User
```bash
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 4. List Sessions
```bash
curl http://localhost:8000/api/auth/sessions/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 5. Validate Session
```bash
curl "http://localhost:8000/api/auth/validate-session/?session_id=$SESSION_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### 6. Logout
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh\": \"$REFRESH_TOKEN\",
    \"session_id\": \"$SESSION_ID\"
  }"
```

---

## 🐛 Troubleshooting

### Q: Tokens not saving to localStorage?
**A:** Check DevTools > Application > Local Storage:
```javascript
localStorage.getItem('access_token')
localStorage.getItem('session_id')
```

### Q: Auto-logout on close not working?
**A:** Check DevTools > Network tab > Close tab:
- Should see POST request to `/api/auth/logout/`
- Check browser console for errors

### Q: Session validation errors?
**A:** Check backend logs:
```bash
python manage.py runserver
# Should see validation requests in logs
```

### Q: Permission denied on admin endpoints?
**A:** Verify user role:
```bash
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer $TOKEN"
# Should show role: "ADMIN"
```

---

## 📚 Documentation

### Start Here
1. **QUICK_START.md** (this file) - 5 minute overview
2. **SECURITY_IMPLEMENTATION_SUMMARY.md** - What was implemented
3. **IMPLEMENTATION_GUIDE.md** - Detailed setup & testing
4. **SECURITY.md** - Complete API reference & best practices

### For Developers
- Read `IMPLEMENTATION_GUIDE.md` for architecture
- Check `backend/accounts/models.py` for UserSession schema
- Review `frontend/src/context/AuthContext.jsx` for session logic
- See `backend/accounts/views.py` for endpoint implementations

### For System Admins
- Review `SECURITY.md` for production deployment checklist
- Check `SECURITY_IMPLEMENTATION_SUMMARY.md` for threat model
- Monitor database for session records
- Set up logging for audit trail

---

## 🎯 What's Next?

### Immediate (Today)
- [ ] Run migrations
- [ ] Test login/logout flow
- [ ] Verify automatic logout on close
- [ ] Test role-based access

### Short Term (This Week)
- [ ] Deploy to staging environment
- [ ] Load test with multiple users
- [ ] Security audit
- [ ] Update production deployment docs

### Medium Term (This Month)
- [ ] Add 2FA/MFA support
- [ ] Implement rate limiting
- [ ] Add audit logging
- [ ] Set up monitoring/alerting

### Long Term (Future)
- [ ] Add IP whitelisting
- [ ] Implement session inactivity timeout
- [ ] Add device trust features
- [ ] Implement anomaly detection

---

## ✨ Summary

You now have:
- ✅ **Secure JWT tokens** with rotation & blacklisting
- ✅ **Automatic logout** on tab close
- ✅ **Session tracking** across devices
- ✅ **Role-based access** (EMPLOYEE vs ADMIN)
- ✅ **Periodic validation** (every 5 minutes)
- ✅ **Password security** (hashed with PBKDF2)
- ✅ **Data privacy** (sensitive fields protected)
- ✅ **Device fingerprinting** (track login locations)

**Users can no longer:**
- ❌ See other users' passwords
- ❌ Access other users' data
- ❌ Stay logged in after closing browser
- ❌ Use revoked tokens
- ❌ Access unauthorized features by role

---

## 📞 Need Help?

1. Check the relevant documentation file
2. Search browser console for error messages
3. Check Network tab for API responses
4. Review database for session records
5. Enable Django DEBUG mode to see detailed errors

---

**Status:** ✅ Ready for Testing & Deployment
**Database Migration:** Required (run `python manage.py migrate`)
**Breaking Changes:** None - fully backward compatible
**New Dependencies:** None - uses existing packages
