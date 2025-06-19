from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)
from sqlalchemy import select

from app.db.models import User
from app.dependencies import (
    AuthUser,
    DatabaseSession,
    RedisClient,
    get_authenticated_user,
)
from app.models.authentication import (
    AuthenticatedResponse,
    CreateUser,
    LoginUser,
    PasswordReset,
    SendResetPassword,
    UserResponse,
)
from app.services.jwt import create_jwt
from app.tasks.email import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get(
    "/session",
    response_model=UserResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def check_session(user: AuthUser):
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=AuthenticatedResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {}, status.HTTP_404_NOT_FOUND: {}},
)
async def login(db_session: DatabaseSession, body: Annotated[LoginUser, Body()]):
    query = select(User).where(User.email == body.email)
    if user := await db_session.scalar(query):
        if user.verified:
            if user.check_password(body.password):
                token = create_jwt(email=body.email)
                response = Response(
                    content=AuthenticatedResponse(
                        access_token=token,
                        token_type="Bearer",
                        user=UserResponse.model_validate(user),
                    )
                )
                response.set_cookie(key="token", value=token)
                return response
            raise HTTPException(
                detail="Incorrect password.", status_code=status.HTTP_401_UNAUTHORIZED
            )
        raise HTTPException(
            detail="Account is unverified.", status_code=status.HTTP_401_UNAUTHORIZED
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@router.get(
    "/logout",
    dependencies=[Depends(get_authenticated_user)],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def logout():
    response = Response(None)
    response.delete_cookie("token")
    return response


@router.post(
    "/create",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Account exists."},
    },
)
async def create_account(
    request: Request,
    db_session: DatabaseSession,
    body: CreateUser,
    background_tasks: BackgroundTasks,
):
    query = select(User).where(User.email == body.email)
    if user := await db_session.scalar(query):
        raise HTTPException(
            detail="Account exists.", status_code=status.HTTP_400_BAD_REQUEST
        )
    user = User(email=body.email, password=body.password)
    db_session.add(user)
    await db_session.commit()
    background_tasks.add_task(
        send_verification_email, email=body.email, base_url=request.base_url
    )
    return Response(None)


@router.get(
    "/verify",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_400_BAD_REQUEST: {}},
)
async def verify_email(
    db_session: DatabaseSession,
    redis: RedisClient,
    token: str = Query(...),
):
    if email := await redis.get(f"verify:{token}"):
        email = email.decode()
        query = select(User).where(User.email == email)
        if user := await db_session.scalar(query):
            user.verified = True
            await db_session.commit()
            await redis.delete(f"verify:{token}")
            return Response(None)
        raise HTTPException(
            detail="Account does not exist.", status_code=status.HTTP_400_BAD_REQUEST
        )
    raise HTTPException(
        detail="Token is not valid.", status_code=status.HTTP_400_BAD_REQUEST
    )


@router.post(
    "/sendreset",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_400_BAD_REQUEST: {}},
)
async def send_reset_email(
    body: Annotated[SendResetPassword, Body()],
    db_session: DatabaseSession,
    background_tasks: BackgroundTasks,
):
    query = select(User).where(User.email == body.email)
    if user := await db_session.scalar(query):
        if user.verified:
            background_tasks.add_task(send_password_reset_email, email=body.email)
            return Response(None)
        raise HTTPException(
            detail="Account is not verified.", status_code=status.HTTP_400_BAD_REQUEST
        )
    raise HTTPException(
        detail="Account does not exist.", status_code=status.HTTP_400_BAD_REQUEST
    )


@router.post(
    "/reset",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_400_BAD_REQUEST: {}},
)
async def reset_password(
    body: Annotated[PasswordReset, Body()],
    db_session: DatabaseSession,
    redis: RedisClient,
):
    if email := await redis.get(f"reset:{body.token}"):
        email = email.decode()
        query = select(User).where(User.email == email)
        if user := await db_session.scalar(query):
            user.set_password(body.password)
            await db_session.commit()
            await redis.delete(f"reset:{body.token}")
            return Response(None)
        raise HTTPException(
            detail="Account does not exist.", status_code=status.HTTP_400_BAD_REQUEST
        )
    raise HTTPException(
        detail="Token is not valid.", status_code=status.HTTP_400_BAD_REQUEST
    )
