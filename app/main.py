import uvicorn
from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.routers.user import user_router
from app.routers.login import login_router

app = FastAPI(
    root_path="/api",
    docs_url="/docs"
)
app.include_router(user_router)
app.include_router(login_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler_custom(request: Request, exc: HTTPException):
    # Access saved body from request state
    body = getattr(request.state, "body", b"")

    # If binary data, provide a different representation
    body_representation = "[Binary Data]" if not body.isascii() else body.decode("utf-8", errors="ignore")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": [
                {
                    "type": "validation_error",
                    "loc": ["body", exc.detail],
                    "msg": str(exc.detail),
                    "input": body_representation,  # Handle non-UTF-8 data gracefully
                }
            ]
        },
    )

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
