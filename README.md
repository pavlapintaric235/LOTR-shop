# LOTR Shop

A full-stack Lord of the Rings themed webshop built with FastAPI, SQLAlchemy, PostgreSQL, Docker, and a minimal frontend.

## Links

- **Live app:** https://lotr-shop.onrender.com
- **GitHub repository:** https://github.com/pavlapintaric235/LOTR-shop

## Project Overview

LOTR Shop is a fantasy-inspired e-commerce application where users can:

- register and log in
- browse product categories
- add products to a cart
- update cart quantities
- checkout and create orders
- simulate payment outcomes
- review order history

An admin user can additionally:

- create categories
- create products
- view all orders
- update order statuses from the frontend

The project combines a REST API backend with a minimal frontend that consumes the same API.

---

## Key Features

### Customer Features
- User registration
- JWT-based login
- Product browsing
- Featured product view
- Category filtering
- Shopping cart management
- Checkout flow
- Order history
- Fake payment simulation

### Admin Features
- Admin-only route protection
- Category creation
- Product creation
- Admin order listing
- Order status updates

### Engineering Features
- FastAPI route organization
- SQLAlchemy async session setup
- PostgreSQL-ready architecture
- Dockerized development workflow
- Alembic migrations
- Demo data bootstrap script
- Render deployment support

---

## Tech Stack

### Backend
- **Python 3.13**
- **FastAPI**
- **SQLAlchemy 2.0**
- **Alembic**
- **PostgreSQL**
- **asyncpg**
- **Pydantic Settings**
- **PyJWT**
- **Passlib**

### Frontend
- **HTML**
- **CSS**
- **Vanilla JavaScript**
- **Jinja2 templates**

### Tooling
- **Docker**
- **Docker Compose**
- **Uvicorn**
- **Black**
- **Flake8**
- **isort**
- **pytest**
- **pytest-cov**
- **pytest-xdist**

### Deployment
- **Render**

---

## Screenshots

> Add your own screenshots under `docs/screenshots/` and keep the filenames below so the README works immediately.

### Homepage
<img width="1833" height="1573" alt="IMG_2604" src="https://github.com/user-attachments/assets/811e3ca5-3e0d-4ea4-816c-c635c40e4878" />

### Cart
<img width="2360" height="1273" alt="IMG_2605" src="https://github.com/user-attachments/assets/9cc4f4f8-858b-42be-803a-36ca07b65349" />


### Orders
<img width="2359" height="851" alt="IMG_2606" src="https://github.com/user-attachments/assets/66e6ee0f-1274-4e49-9215-7cb11c2df2cc" />
<img width="2312" height="849" alt="IMG_2607" src="https://github.com/user-attachments/assets/d15e1804-6499-4814-b28b-6135bb2662c1" />


### Admin Orders


### Login / Signup
<img width="1180" height="583" alt="IMG_2608" src="https://github.com/user-attachments/assets/2142f8f8-74b0-4bd4-be5d-07f90e8f6614" />


### Passed Tests
<img width="569" height="238" alt="image" src="https://github.com/user-attachments/assets/30579326-96d8-403c-b5b1-6ef6dc53a2f7" />



---
## Demo Accounts

If you bootstrap the demo data, these accounts are created:

### Admin
- **Username:** `frodo`
- **Password:** `shire123`

### Customer
- **Username:** `sam`
- **Password:** `shire123`

---

## API Overview

### Auth
- `POST /auth/register`
- `POST /auth/token`

### Users
- `GET /users/me`

### Categories
- `GET /categories`

### Products
- `GET /products`
- `GET /products/{product_id}`
- `GET /homepage`

### Cart
- `GET /cart`
- `POST /cart/items`
- `PUT /cart/items/{item_id}`
- `DELETE /cart/items/{item_id}`

### Orders
- `POST /orders/checkout`
- `GET /orders`
- `GET /orders/{order_id}`

### Payments
- `POST /payments/orders/{order_id}/pay`
- `GET /payments/orders/{order_id}`

### Admin
- `POST /admin/categories`
- `POST /admin/products`
- `GET /admin/orders`
- `GET /admin/orders/{order_id}`
- `PATCH /admin/orders/{order_id}/status`

### Health
- `GET /health`

---

## How It Works

### Authentication
Users register with email, username, and password. Passwords are hashed before storage. Login returns a JWT access token that is then used to access protected routes.

### Catalog
Products belong to categories and can be marked as featured. The frontend can show featured items or filter the catalog by category.

### Cart
Each user has a cart. Items can be added, updated, or removed. Totals are calculated dynamically.

### Orders and Payments
Checkout converts cart items into an order. A fake payment flow is implemented so the project can demonstrate payment handling without using a real payment gateway.

### Admin Flow
Admin users can manage catalog data and order status progression.

---

## Architecture

This project follows a layered structure:

- **API routes** handle HTTP requests and responses
- **Schemas** define request/response validation
- **Services** contain business logic
- **Repositories** handle data access
- **Models** represent database tables
- **Core** contains configuration, security, and shared helpers

This separation keeps the project readable and scalable.
---
## Project Structure

```text
LOTR-shop/
├── alembic/                  # Database migrations
├── app/
│   ├── api/
│   │   └── routes/           # FastAPI route modules
│   ├── core/                 # Config, security, shared utilities
│   ├── db/                   # DB engine, sessions, base setup
│   ├── models/               # SQLAlchemy ORM models
│   ├── repositories/         # Data access layer
│   ├── schemas/              # Pydantic schemas
│   ├── scripts/              # Bootstrap / helper scripts
│   ├── services/             # Business logic layer
│   └── web/
│       ├── static/           # CSS, JS, product images
│       └── templates/        # HTML templates
├── tests/                    # Automated tests
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
├── pyproject.toml
└── README.md
```
