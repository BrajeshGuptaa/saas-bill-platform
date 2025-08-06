import uuid
from contextvars import ContextVar

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import structlog

from app.api.v1.router import api_router
from app.database import Base, engine
from app.logging_config import setup_logging

setup_logging()
logger = structlog.get_logger()
request_id_ctx = ContextVar("request_id", default=None)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Usage-Based Billing Service", version="0.1.0")
static_dir = Path(__file__).parent / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = str(uuid.uuid4())
    request_id_ctx.set(rid)
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    logger.info(
        "request_complete",
        path=request.url.path,
        method=request.method,
        status=response.status_code,
        tenant_id=request.headers.get("X-Tenant-ID"),
        request_id=rid,
    )
    return response


@app.get("/")
def root():
    return {"message": "Usage-based billing service"}


app.include_router(api_router)

# Serve UI at /ui and mount static assets.
@app.get("/ui", include_in_schema=False)
async def ui_entry():
    return FileResponse(static_dir / "index.html")


app.mount("/ui", StaticFiles(directory=static_dir, html=True), name="ui")
