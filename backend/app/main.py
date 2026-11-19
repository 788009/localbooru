import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import config, search, images
from app.indexer import indexer
from app.config import load_config

app = FastAPI(title="Local Booru API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    config_path = os.environ.get("CONFIG_PATH", "../config.toml")
    cfg = load_config(config_path)
    indexer.build(cfg)

app.include_router(config.router)
app.include_router(search.router)
app.include_router(images.router)
