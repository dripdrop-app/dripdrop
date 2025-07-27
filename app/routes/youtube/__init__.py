from fastapi import APIRouter, Depends, status

from app.dependencies import get_authenticated_user
from app.routes.youtube.channels import router as channels_router
from app.routes.youtube.subscriptions import router as subscriptions_router

router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_403_FORBIDDEN: {}},
)
router.include_router(subscriptions_router)
router.include_router(channels_router)
