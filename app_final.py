import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# --- Логирование ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("travel_app")

# --- Настройка из переменной окружения ---
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_NAME = os.getenv("APP_NAME", "Travel Tours API")

app = FastAPI(title=APP_NAME, version=APP_VERSION)

# --- Моковые данные ---
TOURS = [
    {"id": 1, "country": "Италия", "city": "Рим", "price": 1200, "days": 7},
    {"id": 2, "country": "Япония", "city": "Токио", "price": 2500, "days": 10},
    {"id": 3, "country": "Египет", "city": "Хургада", "price": 800, "days": 5},
    {"id": 4, "country": "Франция", "city": "Париж", "price": 1500, "days": 6},
]

BOOKINGS = []

class Booking(BaseModel):
    tour_id: int
    name: str
    email: str

# --- Служебные маршруты ---
@app.get("/health")
def health():
    logger.info("Health check requested")
    return {"status": "ok"}

@app.get("/version")
def version():
    logger.info("Version requested")
    return {"version": APP_VERSION, "app": APP_NAME}

# --- Полезные маршруты по теме ---
@app.get("/")
def root():
    logger.info("Root endpoint accessed")
    return {"message": f"Welcome to {APP_NAME}", "docs": "/docs"}

@app.get("/tours")
def list_tours(
    country: Optional[str] = None,
    max_price: Optional[int] = None,
    max_days: Optional[int] = None,
):
    """Список туров с фильтрами по стране, цене и длительности."""
    logger.info(f"Tours requested: country={country}, max_price={max_price}, max_days={max_days}")
    result = TOURS
    if country:
        result = [t for t in result if t["country"].lower() == country.lower()]
    if max_price:
        result = [t for t in result if t["price"] <= max_price]
    if max_days:
        result = [t for t in result if t["days"] <= max_days]
    return {"count": len(result), "tours": result}

@app.get("/tours/{tour_id}")
def get_tour(tour_id: int):
    """Получить тур по id."""
    logger.info(f"Tour requested: id={tour_id}")
    for t in TOURS:
        if t["id"] == tour_id:
            return t
    logger.warning(f"Tour not found: id={tour_id}")
    raise HTTPException(status_code=404, detail="Tour not found")

@app.post("/bookings")
def create_booking(booking: Booking):
    """Забронировать тур."""
    tour = next((t for t in TOURS if t["id"] == booking.tour_id), None)
    if not tour:
        logger.warning(f"Booking failed: tour {booking.tour_id} not found")
        raise HTTPException(status_code=404, detail="Tour not found")
    new_booking = {
        "id": len(BOOKINGS) + 1,
        "tour_id": booking.tour_id,
        "tour_city": tour["city"],
        "name": booking.name,
        "email": booking.email,
    }
    BOOKINGS.append(new_booking)
    logger.info(f"Booking created: {new_booking['id']} for {booking.name}")
    return {"status": "created", "booking": new_booking}

@app.get("/bookings")
def list_bookings():
    """Все бронирования."""
    logger.info(f"Bookings list requested, total={len(BOOKINGS)}")
    return {"count": len(BOOKINGS), "bookings": BOOKINGS}

@app.get("/stats")
def stats():
    """Статистика по каталогу."""
    logger.info("Stats requested")
    return {
        "total_tours": len(TOURS),
        "total_bookings": len(BOOKINGS),
        "countries": list({t["country"] for t in TOURS}),
    }