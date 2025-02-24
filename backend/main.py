from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth

app = FastAPI()
ORIGINS = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

