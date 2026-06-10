"""Business logic for pandit search, profile management, and earnings."""

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status

from app.models.enums import RoleName
from app.repositories import PanditRepository
from app.schemas import (
    AddPanditServiceRequest,
    AvailabilitySlotResponse,
    CreateAvailabilitySlotRequest,
    PanditEarningsResponse,
    PanditProfileResponse,
    PanditSearchItem,
    UpdatePanditProfileRequest,
)


class PanditServiceManager:
    """Handle pandit-specific workflows on top of repository access."""

    def __init__(self, repo: PanditRepository):
        self.repo = repo
        self.db = repo.db

    async def search(self, *, city_name=None, service_name=None, language_name=None) -> list[PanditSearchItem]:
        """Search approved pandits that match the requested filters."""
        pandits = await self.repo.search_pandits(
            city_name=city_name,
            service_name=service_name,
            language_name=language_name,
        )
        return [self.serialize_search_item(pandit) for pandit in pandits]

    async def get_public_profile(self, pandit_id) -> PanditProfileResponse:
        """Return the public-facing profile for an approved pandit."""
        pandit_profile = await self.repo.get_public_pandit_by_id(pandit_id)
        if not pandit_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pandit not found.")
        return self.serialize_profile(pandit_profile)

    async def get_own_profile(self, current_user) -> PanditProfileResponse:
        """Return the authenticated pandit's own profile."""
        pandit_profile = await self._get_own_pandit_profile(current_user)
        return self.serialize_profile(pandit_profile)

    async def get_slots_by_id(self, pandit_id, current_user) -> list[AvailabilitySlotResponse]:
        """Return a pandit's slots for authenticated end users only."""
        if current_user.role.role_name != RoleName.USER.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only user can view pandit slots.")

        pandit_profile = await self.repo.get_public_pandit_by_id(pandit_id)
        if not pandit_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pandit not found.")

        slots = await self.repo.slots_by_pandit_id(pandit_id)
        return [self.serialize_slot(slot) for slot in slots]

    async def update_profile(self, current_user, payload: UpdatePanditProfileRequest) -> PanditProfileResponse:
        """Update the authenticated pandit's profile and language set."""
        pandit_profile = await self._get_own_pandit_profile(current_user)
        city = None
        if payload.city_name is not None:
            city = await self.repo.get_city_by_name(payload.city_name)
            if not city:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found.")

        languages = await self.repo.get_languages_by_names(payload.language_names)
        normalized_requested = {language_name.strip().lower() for language_name in payload.language_names}
        if len(languages) != len(normalized_requested):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or more languages not found.")

        pandit_profile.user.city_id = city.id if city else None
        pandit_profile.experience_years = payload.experience_years
        pandit_profile.description = payload.description
        await self.repo.replace_pandit_languages(pandit_profile, [language.id for language in languages])
        await self.db.commit()

        updated_profile = await self.repo.get_pandit_profile_by_user_id(current_user.id)
        return self.serialize_profile(updated_profile)

    async def add_service(self, current_user, payload: AddPanditServiceRequest) -> PanditProfileResponse:
        """Add a new service offering or update its price."""
        pandit_profile = await self._get_own_pandit_profile(current_user)
        service = await self.repo.get_service_by_name(payload.service_name)
        if not service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found.")

        existing = await self.repo.get_pandit_service(pandit_profile.id, service.id)
        if existing:
            existing.price = payload.price
        else:
            await self.repo.add_pandit_service(pandit_profile.id, service.id, payload.price)

        await self.db.commit()
        updated_profile = await self.repo.get_pandit_profile_by_user_id(current_user.id)
        return self.serialize_profile(updated_profile)

    async def add_slot(self, current_user, payload: CreateAvailabilitySlotRequest) -> AvailabilitySlotResponse:
        """Create a future, non-overlapping availability slot."""
        pandit_profile = await self._get_own_pandit_profile(current_user)

        if payload.start_time >= payload.end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start time must be before end time.",
            )

        if payload.start_time <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot must be in the future.",
            )

        overlapping_slot = await self.repo.get_overlapping_slot(
            pandit_profile.id,
            payload.start_time,
            payload.end_time,
        )
        # Any overlap is rejected so a pandit cannot advertise double-bookable time.
        if overlapping_slot:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Overlapping slot already exists.",
            )

        slot = await self.repo.create_slot(
            pandit_profile.id,
            payload.start_time,
            payload.end_time,
        )
        await self.db.commit()

        return self.serialize_slot(slot)
    
    async def get_slots(self, current_user) -> list[AvailabilitySlotResponse]:
        """Return the authenticated pandit's availability slots in time order."""
        pandit_profile = await self._get_own_pandit_profile(current_user)
        slots = await self.repo.slots_by_pandit_id(pandit_profile.id)
        return [self.serialize_slot(slot) for slot in slots]

    async def remove_service(self, current_user, service_name: str) -> PanditProfileResponse:
        """Remove one offered service from the authenticated pandit."""
        pandit_profile = await self._get_own_pandit_profile(current_user)
        pandit_service = await self.repo.get_pandit_service_by_name(pandit_profile.id, service_name)
        if not pandit_service:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service offering not found.")

        await self.repo.delete_pandit_service(pandit_service)
        await self.db.commit()
        updated_profile = await self.repo.get_pandit_profile_by_user_id(current_user.id)
        return self.serialize_profile(updated_profile)

   

    async def _get_own_pandit_profile(self, current_user):
        """Validate pandit access and load the caller's linked profile."""
        if current_user.role.role_name != RoleName.PANDIT.value:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pandit access required.")

        pandit_profile = await self.repo.get_pandit_profile_by_user_id(current_user.id)
        if not pandit_profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pandit profile not found.")
        if not pandit_profile.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Pandit account is deactivated.")
        return pandit_profile
    
    async def delete_slot(self, current_user, slot_id: UUID) -> list[AvailabilitySlotResponse]:
        """Delete an availability slot owned by the authenticated pandit."""
        pandit_profile = await self._get_own_pandit_profile(current_user)
        slot = await self.repo.get_slot_by_id(slot_id)
        if not slot or slot.pandit_id != pandit_profile.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found.")

        await self.repo.delete_slot(slot)
        await self.db.commit()


    async def update_slot(self,current_user,slot_id:UUID,payload:CreateAvailabilitySlotRequest) -> AvailabilitySlotResponse:
        pandit_profile=await self._get_own_pandit_profile(current_user)
        slot=await self.repo.get_slot_by_id(slot_id)

        if not slot or slot.pandit_id != pandit_profile.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slot not found.")
        
        slot.start_time=payload.start_time
        slot.end_time=payload.end_time
        await self.db.commit()
        updated_slot=await self.repo.get_slot_by_id(slot_id)
        return self.serialize_slot(updated_slot)


        

    @staticmethod
    def serialize_search_item(pandit_profile) -> PanditSearchItem:
        """Convert a pandit profile model into the public search schema."""
        return PanditSearchItem(
            id=pandit_profile.id,
            user_id=pandit_profile.user_id,
            name=pandit_profile.user.name,
            city_name=pandit_profile.user.city.city_name if pandit_profile.user.city else None,
            experience_years=pandit_profile.experience_years,
            description=pandit_profile.description,
            avg_rating=float(pandit_profile.avg_rating),
            rating_count=pandit_profile.rating_count,
            language_names=[language.language.language_name for language in pandit_profile.languages],
            service_names=[service.service.service_name for service in pandit_profile.services],
        )

    @staticmethod
    def serialize_profile(pandit_profile) -> PanditProfileResponse:
        """Convert a pandit profile model into the detailed profile schema."""
        return PanditProfileResponse(
            id=pandit_profile.id,
            user_id=pandit_profile.user_id,
            name=pandit_profile.user.name,
            email=pandit_profile.user.email,
            phone=pandit_profile.user.phone,
            city_name=pandit_profile.user.city.city_name if pandit_profile.user.city else None,
            experience_years=pandit_profile.experience_years,
            description=pandit_profile.description,
            status=pandit_profile.status.value,
            is_active=pandit_profile.is_active,
            avg_rating=float(pandit_profile.avg_rating),
            rating_count=pandit_profile.rating_count,
            language_names=[language.language.language_name for language in pandit_profile.languages],
            services=[
                {
                    "service_name": service.service.service_name,
                    "price": float(service.price),
                }
                for service in pandit_profile.services
            ],
            ratings=[
                {
                    "rating_id": rating.id,
                    "user_id": rating.user_id,
                    "user_name": rating.user.name,
                    "rating": rating.rating,
                    "review": rating.review,
                }
                for rating in pandit_profile.ratings
            ],
        )

    @staticmethod
    def serialize_slot(slot) -> AvailabilitySlotResponse:
        """Convert a slot model into the API response schema."""
        return AvailabilitySlotResponse(
            id=slot.id,
            pandit_id=slot.pandit_id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            is_booked=slot.is_booked,
        )
