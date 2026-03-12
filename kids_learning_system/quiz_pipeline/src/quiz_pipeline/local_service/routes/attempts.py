from fastapi import APIRouter, HTTPException
from pydantic import ValidationError
from ..models import AttemptPayload
from ..services.attempt_store import save_attempt, list_attempts


router = APIRouter(prefix="/api")

@router.post("/attempts")
def post_attempt(payload: AttemptPayload):
    try:
        file_path = save_attempt(payload)
        return {"status": "saved", "path": file_path}
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save attempt: {e}")

@router.get("/attempts/{child_id}")
def get_attempts(child_id: str):
    try:
        attempts = list_attempts(child_id)
        return {"attempts": [a.dict() for a in attempts]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list attempts: {e}")
