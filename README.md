# Office Lunch Ordering System

A full-stack demo app: employees log in, browse the day's lunch menu, add items
to a cart, check out, pay via a static UPI QR code, and submit the UTR
(transaction reference) number. Admins manage the menu, verify payments, and
track orders from a simple dashboard.

**Stack:** Django REST Framework + PostgreSQL + JWT (backend), React + Vite +
Tailwind (frontend).

---

## Quick start (Docker)

```bash
docker compose up --build
```

This starts:
- PostgreSQL on `localhost:5432`
- Django API on `http://localhost:8000`
- React app on `http://localhost:5173`

Then, in a second terminal, create an admin account and seed sample menu data:

```bash
docker compose exec backend python manage.py promote_admin \
  --email admin@company.com --create --password "AdminPass123" --full-name "Canteen Admin"

docker compose exec backend python manage.py seed_demo_data
```

Open `http://localhost:5173`:
- Sign up as an employee, log in, and order from today's seeded menu.
- Log in as admin (`admin@company.com` / `AdminPass123`) to manage menu/orders.
- Upload a payment QR image from **Order Management → Upload Payment QR Code**
  before employees check out (otherwise the QR step shows "not configured yet").

---

## Manual setup (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DATABASE_URL to point at your local PostgreSQL instance

python manage.py migrate
python manage.py promote_admin --email admin@company.com --create --password "AdminPass123" --full-name "Admin"
python manage.py seed_demo_data
python manage.py runserver
```

API runs at `http://localhost:8000/api/`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # defaults to http://localhost:8000/api
npm run dev
```

App runs at `http://localhost:5173`.

---

## Key API routes

| Purpose                  | Method & Path                                |
|---------------------------|-----------------------------------------------|
| Employee register         | `POST /api/auth/register/`                    |
| Employee login             | `POST /api/auth/login/employee/`              |
| Admin login                 | `POST /api/auth/login/admin/`                 |
| Refresh token               | `POST /api/auth/token/refresh/`               |
| Today's menu (employee)     | `GET /api/menu/today/`                        |
| Catalog CRUD (admin)         | `/api/menu/items/`, `/api/menu/items/<id>/`   |
| Daily menu CRUD (admin)      | `/api/menu/daily/`, `/api/menu/daily/<id>/`   |
| Checkout (place order)       | `POST /api/orders/checkout/`                  |
| Submit UTR                    | `POST /api/orders/<id>/submit-utr/`           |
| My order history               | `GET /api/orders/my-orders/`                  |
| Active payment QR               | `GET /api/orders/payment-qr/`                 |
| Admin: all orders                | `GET /api/orders/admin/orders/`               |
| Admin: update order status        | `PATCH /api/orders/admin/orders/<id>/status/` |
| Admin: upload payment QR            | `POST /api/orders/admin/payment-qr/`          |
| Admin: dashboard stats               | `GET /api/orders/admin/dashboard/`            |

## Notes

- Employees self-register; admin accounts are created only via the
  `promote_admin` management command (no public admin signup).
- Cart state lives entirely in the frontend (React context); the whole cart
  is submitted as one order at checkout.
- Payment has no real gateway — it's a static QR image the admin uploads,
  paired with a manual UTR entry that an admin later confirms or rejects.
- Order cutoff time defaults to 11:00 (`ORDER_CUTOFF_HOUR` in `.env`), or can
  be set per day via `cutoff_time` on a `DailyMenu`.
