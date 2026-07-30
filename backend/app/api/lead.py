"""
app/api/lead.py
---------------
POST /api/lead — direct lead submission
GET  /api/lead/health — check PostgreSQL connection
"""

import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import LeadRequest, LeadResponse
from app.utils.database import save_lead, engine
from sqlalchemy import text

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/lead", tags=["leads"])


@router.post("/", response_model=LeadResponse)
async def submit_lead(req: LeadRequest):
    try:
        result = await save_lead(
            session_id=req.session_id,
            name=req.name,
            email=req.email,
            requirement=req.requirement,
            phone=req.phone,
        )
        lead_id = result.get("id")
        logger.info(f"Lead submitted: {req.email}")
        return LeadResponse(
            success=True,
            lead_id=str(lead_id),
            message=f"Thanks {req.name}! We'll be in touch at {req.email} soon.",
        )
    except Exception as e:
        logger.error(f"Lead submission error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save lead.")


@router.get("/health")
async def lead_db_health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"postgres": "connected"}
    except Exception as e:
        return {"postgres": "error", "detail": str(e)}