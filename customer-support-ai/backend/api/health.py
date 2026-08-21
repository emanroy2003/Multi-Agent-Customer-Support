from fastapi import APIRouter

from backend.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env,
        "database_type": settings.database_type,
        "llm_provider": settings.llm_provider,
    }
