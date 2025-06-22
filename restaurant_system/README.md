# Restaurant Management System

## Features
- Menu management with categories
- Table reservation system with availability checks
- Order processing (Pending → Paid)
- Real-time inventory tracking with alerts
- Daily sales reports
- Django Admin dashboard

## Setup
1. Install requirements: `pip install -r requirements.txt`
2. Configure PostgreSQL in `settings.py`
3. Run migrations: `python manage.py migrate`
4. Start server: `python manage.py runserver`

## API Endpoints
| Endpoint         | Method | Description                |
|------------------|--------|----------------------------|
| /api/menu/       | GET    | List available menu items |
| /api/orders/     | POST   | Place new order           |
| /api/reservations| POST   | Create reservation        |
| /admin/          | GET    | Admin dashboard           |