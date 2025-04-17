from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.v1 import ping
from core.config import settings
from routers.v1.auth import router as auth_router
from routers.v1.user import router as user_router

app = FastAPI(
    title="OrderMe Pre-Order Platform",
    description="API for managing pre-orders with user authentication, product management, and order processing",
    version="0.1.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)


DATABASE_URL = settings.DATABASE_URL
DATABASE_URL_TEST = settings.DATABASE_URL_TEST

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ping.router, prefix="/api/v1")
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/api/v1")
  # Add the auth router
# Include additional routers as you develop them
# app.include_router(users.router, prefix="/api/v1")
# app.include_router(products.router, prefix="/api/v1")
# app.include_router(orders.router, prefix="/api/v1")

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the OrderMe Pre-Order Platform API",
        "documentation": "/api/v1/docs",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)