from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo

router = APIRouter()


class DefaultFullnessBody(BaseModel):
    value: float


@router.get("/settings")
def settings():
    d = settings_repo.get_all()
    d["default_fullness"] = settings_repo.get_default_fullness()
    return d


@router.put("/settings/default_fullness")
def put_default_fullness(body: DefaultFullnessBody):
    try:
        v = settings_repo.set_default_fullness(body.value)
    except (TypeError, ValueError):
        raise HTTPException(400, "default_fullness must be a positive number")
    return {"default_fullness": v}
