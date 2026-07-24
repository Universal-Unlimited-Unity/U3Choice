from fastapi import FastAPI
from .endpoints.authentification import auth_router
from .endpoints.users import router as users_router
from .endpoints.friendships import router as friendships_router
from database import metadata, eng
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    metadata.create_all(eng, checkfirst=True)
    yield
    metadata.drop_all(eng)
    print("Shutting down...")

app = FastAPI(title="Social Media API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://172.18.0.2:5173",  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(friendships_router)
app.include_router(auth_router)