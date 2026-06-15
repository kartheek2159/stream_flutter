from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
from db.base import Base
from routes import auth,upload,video
from db.database import engine

app= FastAPI()

origins=["http://localhost","https://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,prefix="/auth")
app.include_router(upload.router,prefix="/upload/video")
app.include_router(video.router,prefix="/videos")

@app.get("/")
def root():
    return "hello world!!"

Base.metadata.create_all(bind=engine)