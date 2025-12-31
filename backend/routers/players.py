from fastapi import APIRouter, Depends

from backend.auth import get_current_user
from backend.models import PlayerInfo

router = APIRouter()


@router.get("/api/players")
def players_endpoint(user=Depends(get_current_user)):
    sample = [
        PlayerInfo(
            name="Steve",
            uuid="0000-1111",
            skin_url="https://textures.minecraft.net/texture/sample",
            session_seconds=1200,
            position={"x": 0.0, "y": 64.0, "z": 0.0},
        ),
    ]
    return sample
