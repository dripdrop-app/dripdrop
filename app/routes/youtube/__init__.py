from fastapi import APIRouter, Depends, status

from app.dependencies import get_authenticated_user

api = APIRouter(
    prefix="/youtube",
    tags=["YouTube"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_403_FORBIDDEN: {}},
)
