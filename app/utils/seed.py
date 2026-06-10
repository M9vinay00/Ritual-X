"""Seed helpers for reference data and the optional super admin account."""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.database import AsyncSessionLocal
from app.models import City, Language, Role, Service, State
from app.models.enums import RoleName
from app.models.User import User

LOCATION_SEED_DATA = [
    {
        "state_name": "Gujarat",
        "default_language": "Gujarati",
        "cities": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
    },
    {
        "state_name": "Maharashtra",
        "default_language": "Marathi",
        "cities": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane"],
    },
    {
        "state_name": "Rajasthan",
        "default_language": "Hindi",
        "cities": ["Jaipur", "Udaipur", "Jodhpur", "Kota", "Ajmer"],
    },
    {
        "state_name": "Uttar Pradesh",
        "default_language": "Hindi",
        "cities": ["Lucknow", "Varanasi", "Kanpur", "Prayagraj", "Agra"],
    },
    {
        "state_name": "Madhya Pradesh",
        "default_language": "Hindi",
        "cities": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"],
    },
]

LANGUAGE_SEED_DATA = [
    "Hindi",
    "English",
    "Gujarati",
    "Marathi",
    "Sanskrit",
]

SERVICE_SEED_DATA = [
    "Griha Pravesh",
    "Satyanarayan Katha",
    "Vivah Puja",
    "Mundan Sanskar",
    "Naamkaran",
    "Vastu Puja",
    "Navgraha Shanti",
    "Pitru Dosh Nivaran",
]


async def seed_roles(db: AsyncSession):
    """Ensure the core platform roles exist."""
    roles = [RoleName.ADMIN.value, RoleName.USER.value, RoleName.PANDIT.value]

    for role_name in roles:
        result = await db.execute(select(Role).where(Role.role_name == role_name))
        existing_role = result.scalar_one_or_none()

        if not existing_role:
            db.add(Role(role_name=role_name))

    await db.commit()


async def seed_locations(db: AsyncSession):
    """Seed states and their supported cities."""
    for state_data in LOCATION_SEED_DATA:
        state_result = await db.execute(select(State).where(State.state_name == state_data["state_name"]))
        state = state_result.scalar_one_or_none()

        if not state:
            state = State(
                state_name=state_data["state_name"],
                default_language=state_data["default_language"],
            )
            db.add(state)
            # Flush so the newly created state id is available for city inserts below.
            await db.flush()

        for city_name in state_data["cities"]:
            city_result = await db.execute(
                select(City).where(City.state_id == state.id, City.city_name == city_name)
            )
            city = city_result.scalar_one_or_none()
            if not city:
                db.add(City(state_id=state.id, city_name=city_name))

    await db.commit()


async def seed_languages(db: AsyncSession):
    """Ensure supported languages exist."""
    for language_name in LANGUAGE_SEED_DATA:
        result = await db.execute(select(Language).where(Language.language_name == language_name))
        existing_language = result.scalar_one_or_none()
        if not existing_language:
            db.add(Language(language_name=language_name))

    await db.commit()


async def seed_services(db: AsyncSession):
    """Ensure supported service names exist."""
    for service_name in SERVICE_SEED_DATA:
        result = await db.execute(select(Service).where(Service.service_name == service_name))
        existing_service = result.scalar_one_or_none()
        if not existing_service:
            db.add(Service(service_name=service_name))

    await db.commit()


async def seed_admin(db: AsyncSession):
    """Create the configured super admin account when enabled."""
    await seed_roles(db)

    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return "ADMIN_EMAIL and ADMIN_PASSWORD are not configured. Admin seed skipped."

    existing_admin = await db.execute(select(User.id).where(User.is_super_admin.is_(True)))
    if existing_admin.scalar_one_or_none():
        return "Super admin already exists. Seed skipped."

    admin_role_result = await db.execute(select(Role).where(Role.role_name == RoleName.ADMIN.value))
    admin_role = admin_role_result.scalar_one_or_none()
    if not admin_role:
        return "Admin role is missing. Seed skipped."

    db.add(
        User(
            name=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            phone=settings.ADMIN_PHONE,
            password=hash_password(settings.ADMIN_PASSWORD),
            role_id=admin_role.id,
            is_active=True,
            is_super_admin=True,
        )
    )
    await db.commit()
    return "Super admin created successfully."


async def run_master_seed():
    """Run all reference data seeds in one command."""
    async with AsyncSessionLocal() as db:
        await seed_roles(db)
        await seed_locations(db)
        await seed_languages(db)
        await seed_services(db)
        print("Roles, locations, languages, and services seeded successfully.")


async def run_admin_seed():
    """Run only the optional super admin seed."""
    async with AsyncSessionLocal() as db:
        message = await seed_admin(db)
        print(message)


if __name__ == "__main__":
    asyncio.run(run_master_seed())
