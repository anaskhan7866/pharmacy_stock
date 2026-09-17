# Thought Process & Reasoning

## Architecture & Tech Stack
Given the strict 2.5-hour time limit, I chose **Django** and **Django REST Framework (DRF)** with an **SQLite** database. Django provides built-in user authentication, an immediate admin interface for rapid data entry, and robust ORM capabilities, which allowed me to focus purely on the core business logic rather than writing boilerplate code. Bootstrap was used for the frontend to ensure a clean, responsive UI without wasting time on custom CSS.

## The FEFO Dispense Logic
The core requirement was to dispense oldest-first (First-Expiry-First-Out) and never dispense expired stock. 
1. **Database Level:** The `Batch` model enforces strict ordering via `ordering = ['expiry_date']` in its Meta class.
2. **Filtering Level:** The `total_sellable_stock` method on the `Medicine` model dynamically filters out any batch where `expiry_date <= today`.
3. **Dispense Execution:** When a dispense request hits the `/api/medicines/<id>/dispense/` endpoint, it loops through only valid batches, subtracting the requested quantity sequentially. If a batch runs out, it moves to the next valid batch until the order is fulfilled.

## Testing & Issue Resolution
I tested the logic by creating a mix of expired, soon-to-expire, and far-future batches. 
- **Issue:** Initially, it was possible for the API to attempt dispensing from an empty batch if the quantity reached zero but the date was valid. 
- **Fix:** I updated the queryset filter in the API view to `quantity__gt=0` alongside the date validation, ensuring zero-quantity batches are entirely ignored by the loop.
