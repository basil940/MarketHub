# 🛍️ MarketHub — Full-Stack E-Commerce Platform

> A production-style e-commerce platform built with Django REST Framework, featuring real-time order tracking, Stripe payments, a loyalty rewards system, and a live admin dashboard powered by WebSockets — all served through a vanilla HTML/CSS/JS frontend.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-API-red)
![Channels](https://img.shields.io/badge/Django%20Channels-WebSockets-orange)
![Stripe](https://img.shields.io/badge/Stripe-Payments-purple?logo=stripe&logoColor=white)
![JWT](https://img.shields.io/badge/Auth-JWT-black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| | Feature |
|---|---|
| 🔐 | **JWT Authentication** — register/login with access & refresh tokens |
| 🛒 | **Product Catalog** — search, category filters, sorting, live inventory |
| 🧺 | **Shopping Cart** — add/update/remove items with stock validation |
| 📦 | **Orders & Tracking** — status timeline, cancellation, shipping address |
| ❤️ | **Wishlist** — save products, move to cart in one click |
| ⭐ | **Reviews & Ratings** — 5-star reviews gated to verified (delivered) purchasers |
| 💳 | **Stripe Checkout** — hosted payment flow with webhook-verified confirmation |
| 🎁 | **Loyalty Points** — earn 20 pts per ₹100 spent, redeem at 1 pt = ₹2 (up to 50% off) |
| 📊 | **Live Admin Dashboard** — real-time revenue chart, top products, live activity feed via WebSocket |
| ✉️ | **Email Notifications** — welcome, order confirmation, payment confirmation, cancellation (SMTP) |

---

## 🏗️ System Architecture

```
Browser (HTML/CSS/JS) ──fetch──► Django REST Framework API
        │                              │
        │                    ┌─────────┴─────────┐
        │                    │   JWT Auth Layer    │
        │                    └─────────┬─────────┘
        │                              │
        │                 ┌────────────┼────────────┬──────────────┐
        │                 │            │            │              │
        │              Products      Orders       Cart         Loyalty
        │             (Reviews)   (Tracking)                 (Points)
        │                              │
        │                    ┌─────────┴─────────┐
        │                    │   Stripe Checkout   │
        │                    │  + Webhook Handler  │
        │                    └─────────┬─────────┘
        │                              │
        ▼                              ▼
WebSocket (Channels) ◄──── broadcast_dashboard() ──── Order/Payment events
        │
        ▼
Live Admin Dashboard (Chart.js + real-time feed)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, Django 5.2, Django REST Framework |
| Real-time | Django Channels (WebSockets), Daphne (ASGI server) |
| Auth | djangorestframework-simplejwt |
| Payments | Stripe API + Stripe CLI (local webhook forwarding) |
| Email | SMTP via Gmail (`python-decouple` for secrets) |
| Database | SQLite (development) |
| Frontend | Vanilla HTML / CSS / JavaScript, Chart.js |
| Config | `python-decouple` (`.env` for secrets) |

---

## 📁 Project Structure

```
ecom_project/
├── cart/            # Cart — add/update/remove items
├── dashboard/        # Live admin dashboard — stats API + WebSocket consumer
├── ecomsite/         # Project settings, URLs, email utilities
├── loyalty/          # Loyalty points — earn/redeem logic
├── orders/           # Orders, tracking, Stripe checkout & webhook
├── products/         # Products, categories, inventory, reviews
├── users/            # Auth — register, login, profile
├── wishlist/         # Wishlist toggle and listing
├── templates/        # Frontend HTML pages (served by Django)
├── static/js/        # Frontend JavaScript (api.js)
└── media/            # Uploaded product/category images
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/basil940/MarketHub.git
cd MarketHub
```

### 2. Set up the virtual environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```
SECRET_KEY=your-django-secret-key
DEBUG=True
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
DEFAULT_FROM_EMAIL=MarketHub <your_email@gmail.com>
```

### 4. Run migrations & create an admin user

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Start the servers

**Terminal 1 — Django (ASGI/Daphne):**
```bash
python manage.py runserver
```

**Terminal 2 — Stripe CLI (local webhook forwarding):**
```bash
stripe listen --forward-to http://127.0.0.1:8000/api/orders/webhook/
```

Visit:
- **Store** → `http://127.0.0.1:8000/`
- **Live Dashboard** (admin/staff only) → `http://127.0.0.1:8000/dashboard/`
- **Django Admin** → `http://127.0.0.1:8000/admin/`

---

## 💳 Testing Payments

Use Stripe's test card:

```
Card number: 4242 4242 4242 4242
Expiry:      any future date
CVC:         any 3 digits
```

---

## 🔑 Key Design Decisions

- **Server-rendered frontend** — HTML pages served directly via Django `TemplateView` rather than a separate SPA, avoiding CORS issues with media files and simplifying deployment.
- **Payment integrity** — orders are created `unpaid`; status only flips to `paid` after Stripe's webhook confirms `checkout.session.completed`, so an order can never be marked paid without verified payment.
- **Live dashboard without polling** — Django Channels broadcasts `new_order` and `payment_confirmed` events to a WebSocket group; the dashboard updates instantly, with a 15s poll as a fallback safety net.
- **Trustworthy reviews** — only users with a `delivered` order containing the product can leave a review, preventing fake reviews.

---

## 📸 Screenshots

*(Add screenshots of the homepage, product detail page, cart, and live dashboard here)*

---

## 👤 Author

**Basil Paul**

---

## 📄 License

This project is licensed under the **MIT License**.