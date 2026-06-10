"""Pandit-facing and public pandit discovery API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.database import get_db
from app.dependencies import get_current_active_user
from app.models.enums import RoleName
from app.repositories import PanditRepository
from app.schemas import (
    AddPanditServiceRequest,
    ApiResponse,
    AvailabilitySlotResponse,
    CreateAvailabilitySlotRequest,
    PanditEarningsResponse,
    PanditProfileResponse,
    PanditSearchItem,
    UpdatePanditProfileRequest,
)
from app.services import PanditServiceManager

router = APIRouter(prefix="/pandits", tags=["Pandits"])


def get_pandit_service(db=Depends(get_db)) -> PanditServiceManager:
    """Build the pandit service with a request-scoped repository."""
    return PanditServiceManager(PanditRepository(db))


@router.get("/search", response_model=ApiResponse[list[PanditSearchItem]])
async def search_pandits(
    city_name: str | None = Query(default=None),
    service_name: str | None = Query(default=None),
    language_name: str | None = Query(default=None),
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Search approved pandits using optional city, service, and language filters."""
    if current_user.role.role_name != RoleName.USER.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only user can search pandits.")
    effective_language_name = language_name
    # Fall back to the user's preferred language when the client omits the filter.
    if not effective_language_name and current_user.preferred_language:
        effective_language_name = current_user.preferred_language.language_name

    pandits = await service.search(
        city_name=city_name,
        service_name=service_name,
        language_name=effective_language_name,
    )
    return ApiResponse(message="Pandits fetched successfully.", data=pandits)


@router.get("/profile", response_model=ApiResponse[PanditProfileResponse])
async def get_own_pandit_profile(
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Return the authenticated pandit's own profile."""
    pandit_profile = await service.get_own_profile(current_user)
    return ApiResponse(message="Pandit profile fetched successfully.", data=pandit_profile)


@router.put("/profile", response_model=ApiResponse[PanditProfileResponse])
async def update_pandit_profile(
    payload: UpdatePanditProfileRequest,
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Update the authenticated pandit's profile details."""
    pandit_profile = await service.update_profile(current_user, payload)
    return ApiResponse(message="Pandit profile updated successfully.", data=pandit_profile)


@router.post("/slots", response_model=ApiResponse[AvailabilitySlotResponse])
async def create_availability_slot(
    payload: CreateAvailabilitySlotRequest,
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Create a future availability slot for the authenticated pandit."""
    slot = await service.add_slot(current_user, payload)
    return ApiResponse(message="Availability slot created successfully.", data=slot)

@router.get("/slots", response_model=ApiResponse[list[AvailabilitySlotResponse]])
async def get_own_slots(
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Return all availability slots owned by the authenticated pandit."""
    slots = await service.get_slots(current_user)
    return ApiResponse(message="Availability slots fetched successfully.", data=slots)


@router.post("/services", response_model=ApiResponse[PanditProfileResponse])
async def add_pandit_service(
    payload: AddPanditServiceRequest,
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Add or update a service offering for the authenticated pandit."""
    pandit_profile = await service.add_service(current_user, payload)
    return ApiResponse(message="Service added successfully.", data=pandit_profile)


@router.delete("/services/{service_name}", response_model=ApiResponse[PanditProfileResponse])
async def remove_pandit_service(
    service_name: str,
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Remove a service offering from the authenticated pandit."""
    pandit_profile = await service.remove_service(current_user, service_name)
    return ApiResponse(message="Service removed successfully.", data=pandit_profile)




@router.get("/{pandit_id}/slots", response_model=ApiResponse[list[AvailabilitySlotResponse]])
async def get_pandit_slots_by_id(
    pandit_id: UUID,
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Return a pandit's slots for authenticated end users."""
    slots = await service.get_slots_by_id(pandit_id, current_user)
    return ApiResponse(message="Pandit slots fetched successfully.", data=slots)


@router.get("/{pandit_id}", response_model=ApiResponse[PanditProfileResponse])
async def get_pandit_public_profile(pandit_id: UUID, service: PanditServiceManager = Depends(get_pandit_service)):
    """Return the public-facing profile of an approved pandit."""
    pandit_profile = await service.get_public_profile(pandit_id)
    return ApiResponse(message="Pandit profile fetched successfully.", data=pandit_profile)


@router.delete("/slots/{slot_id}")
async def delete_availability_slot(
    slot_id: UUID,
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Delete an availability slot owned by the authenticated pandit."""
    slots = await service.delete_slot(current_user, slot_id)
    return ApiResponse(message=" slot deleted successfully.", data=slots)

@router.put("/slots/{slot_id}", response_model=ApiResponse[AvailabilitySlotResponse])
async def update_availability_slot(
    slot_id: UUID,
    payload: CreateAvailabilitySlotRequest,
    current_user=Depends(get_current_active_user),
    service: PanditServiceManager = Depends(get_pandit_service),
):
    """Update the time range of an availability slot owned by the authenticated pandit."""
    slot = await service.update_slot(current_user, slot_id, payload)
    return ApiResponse(message="Availability slot updated successfully.", data=slot)