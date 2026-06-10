from .admin import router as admin_router
from .auth import router as auth_router
from .pandits import router as pandits_router
from .users import router as users_router
from .booking import router as booking_router 
from .payment import router as payment_router
from .rating import router as rating_router


__all__ = ["admin_router", "auth_router", "pandits_router", "users_router", "booking_router", "payment_router", "rating_router"]
