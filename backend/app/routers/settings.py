from fastapi import APIRouter, HTTPException
from app.repositories import settings_repo
from app.schemas.settings import SettingsUpdate

router = APIRouter()

@router.get("/settings")
def settings(): return settings_repo.get_public()

@router.put("/settings")
def update_settings(body: SettingsUpdate):
    try:
        settings_repo.set_default_fullness(body.default_fullness)
    except ValueError as e:
        raise HTTPException(422, str(e))
    return settings_repo.get_public()
