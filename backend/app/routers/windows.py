from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo, windows as repo

router = APIRouter()


class WindowFullnessBody(BaseModel):
    fullness: float | None = None


def _with_effective(r: dict):
    eff, src = settings_repo.resolve_fullness(r)
    return {**r, "effective_fullness": eff, "fullness_source": src}


@router.get("/windows")
def list_windows(): return {"items": repo.list_windows()}


@router.get("/windows/{wid}")
def get_window(wid: int):
    r = repo.get_window(wid)
    if not r: raise HTTPException(404)
    return _with_effective(r)


@router.put("/windows/{wid}/fullness")
def set_window_fullness(wid: int, body: WindowFullnessBody):
    if body.fullness is not None and body.fullness <= 0:
        raise HTTPException(400, "fullness must be positive")
    if not repo.set_fullness(wid, body.fullness):
        raise HTTPException(404)
    return _with_effective(repo.get_window(wid))
