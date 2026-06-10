"""Enumerations shared across models and business logic."""

from enum import Enum

from sqlalchemy import Enum as SqlEnum


class PanditProfileStatus(str, Enum):
    """Approval states for pandit onboarding."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class RoleName(str, Enum):
    """Supported application roles."""

    ADMIN = "admin"
    USER = "user"
    PANDIT = "pandit"


class BookingStatus(str, Enum):
    """Lifecycle states for a booking."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, Enum):
    """Status values for payment processing and settlement."""

    PENDING = "pending"
    PAID = "paid"
    COMPLETED = "completed"
    FAILED = "failed"


class PaymentMethod(str, Enum):
    """Supported payment methods."""

    CASH = "cash"
    UPI = "upi"
    ONLINE = "online"


def enum_values(enum_class):
    """Return enum values in the format SQLAlchemy expects."""
    return [item.value for item in enum_class]


def db_enum(enum_class, name):
    """Create a database-friendly SQLAlchemy enum backed by string values."""
    return SqlEnum(
        enum_class,
        name=name,
        native_enum=False,
        create_constraint=True,
        values_callable=enum_values,
    )
