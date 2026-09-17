# Pharmacy FEFO Inventory Engine

A full-stack Django application designed to manage pharmacy stock using strict First-Expiry-First-Out (FEFO) dispensing logic. This ensures expired medicines are never dispensed, protecting patients and minimizing waste.

## Setup and Run Instructions

1. **Clone the repository:**
   `git clone https://github.com/b231010-ship-it/pharmacy_stock.git`
   `cd pharmacy_stock`

2. **Create and activate a virtual environment:**
   `python -m venv venv`
   `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)

3. **Install dependencies:**
   `pip install -r requirements.txt`

4. **Apply database migrations:**
   `python manage.py migrate`

5. **Create a superuser (for admin access):**
   `python manage.py createsuperuser`

6. **Run the server:**
   `python manage.py runserver`

7. **Access the application:**
   - Landing Page: `http://127.0.0.1:8000/`
   - Interactive Dashboard: `http://127.0.0.1:8000/dashboard/`
   - Admin Panel: `http://127.0.0.1:8000/admin/`

## REST API Endpoints

- `GET /api/medicines/` : List all medicines (includes search and pagination).
- `POST /api/medicines/` : Create a new medicine category.
- `GET /api/batches/` : List all batches (includes search and ordering).
- `POST /api/batches/` : Add a new medicine batch with an expiry date.
- `POST /api/medicines/<id>/dispense/` : Custom endpoint to dispense a specific quantity of a medicine. Expects JSON: `{"quantity": 10}`.

**Author:** Annus Khan
