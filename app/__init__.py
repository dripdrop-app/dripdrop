from fastapi import APIRouter, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from app.routes.authentication import router as auth_router
from app.routes.music import router as music_router
from app.routes.youtube import router as youtube_router
from app.settings import ENV, settings

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(music_router)
api_router.include_router(youtube_router)


app = FastAPI(title="dripdrop", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.include_router(api_router)


origins = []
if settings.env == ENV.DEVELOPMENT:
    origins.append("http://localhost:8080")
    origins.append("http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthcheck")
async def health_check():
    return Response(None, 200)
