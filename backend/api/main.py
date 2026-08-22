from fastapi import FastAPI
from .endpoints.authentification import auth_router
from .endpoints.users import router as users_router
from .endpoints.friendships import router as friendships_router
from .endpoints.search_engine import search_router
from .endpoints.messages import router as messages_router
from database import init_db
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from .endpoints.notifications_ws import router as notifications_router
from .endpoints.security import router as security_router
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    try:
        await init_db()
    except Exception:
        logger.critical("Database did not start seccussfully")
    yield
    print("Shutting down...")

app = FastAPI(title="U3Choice API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(friendships_router)
app.include_router(auth_router)
app.include_router(search_router)
app.include_router(notifications_router)
app.include_router(messages_router)
app.include_router(security_router)