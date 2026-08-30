import time

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from contextlib import asynccontextmanager

from app.api.routes import router as api_router
from app.config import logger
from app.db.connection import check_db_connection, close_db_pool, init_db_pool


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    init_db_pool()
    yield
    close_db_pool()


app = FastAPI(
    title="MigrantAid API",
    description="An evidence-backed case-to-action assistant for supporting migrant workers",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    path = request.url.path
    method = request.method

    logger.debug(f"Received request: {method} {path}")

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Processed request: {method} {path} - Status: {response.status_code} - Latency: {process_time:.2f}ms"
        )
        return response
    except Exception as e:  # noqa: BLE001
        process_time = (time.time() - start_time) * 1000
        logger.error(
            f"Failed request: {method} {path} - Error: {e!s} - Latency: {process_time:.2f}ms",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An internal server error occurred."},
        )


# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP exception: status={exc.status_code}, detail={exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error for request: errors={exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc!s}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred."},
    )


# Include API Router
app.include_router(api_router)


# Health Check Endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    db_ok = check_db_connection()
    return {
        "status": "ok",
        "database": "connected" if db_ok else "disconnected",
    }

