"""FastAPI web application main entry point."""
import logging

from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.database import init_db, get_db
from shared.redis import init_redis
from shared.services.user_service import UserService
from shared.logging_config import setup_logging, get_logger
from shared.error_handlers import setup_error_handlers
from shared.services.scheduler_service import scheduler

from webapp.middleware.auth import AuthMiddleware, get_current_telegram_user
from webapp.routers import auth

from webapp.routers import user, loyalty, referral, order, wallet

from typing import Optional
from fastapi import HTTPException
# Setup logging system
setup_logging()
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Telegram Bar Bot API",
    description="API for Telegram Bar Bot with loyalty program",
    version="0.1.0",
    debug=settings.debug
)

# Setup error handlers
setup_error_handlers(app)

# Add Telegram Web App authentication middleware
app.add_middleware(AuthMiddleware)

# Include API routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(loyalty.router)
app.include_router(referral.router)
# app.include_router(menu.router)
app.include_router(order.router)
app.include_router(wallet.router)

# Setup Jinja2 templates
templates = Jinja2Templates(directory="webapp/templates")


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    logger.info("Starting application...")
    # Initialize database tables
    await init_db()
    logger.info("Database initialized")
    await init_redis()
    logger.info("Cache initialized")
    
    # Start background scheduler
    await scheduler.start()
    logger.info("Background scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown."""
    logger.info("Shutting down application...")
    # Stop background scheduler
    await scheduler.stop()
    logger.info("Background scheduler stopped")
    


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Telegram Bar Bot API",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/clear-cache")
async def clear_cache(
    request: Request,
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """Clear application cache (admin only)."""
    try:
        logger.info(f"Clear cache request from user: {telegram_user}")
        
        # Проверяем, что пользователь админ
        user_id = telegram_user.get("id")
        admin_ids = [int(id.strip()) for id in settings.admin_telegram_ids.split(",") if id.strip()]
        
        if user_id not in admin_ids:
            logger.warning(f"Access denied for user {user_id} to clear cache")
            return {"error": "Access denied", "status": "error"}
        
        import os
        import time
        
        # Генерируем новый timestamp для cache busting
        cache_version = str(int(time.time()))
        
        # Сохраняем версию в файл
        with open("/app/static_version.txt", "w") as f:
            f.write(cache_version)
        
        logger.info(f"Cache cleared by admin {user_id}, new version: {cache_version}")
        
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "cache_version": cache_version,
            "timestamp": cache_version
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}", exc_info=True)
        return {"error": str(e), "status": "error"}


# # Template routes for Mini App pages
# @app.get("/app")
# async def app_entry(request: Request):
#     """Main app entry point."""
#     try:
#         logger.info(f"App entry request from {request.client.host if request.client else 'unknown'}")
#         logger.info(f"Request path: {request.url.path}")
#         logger.info(f"Request headers: {dict(request.headers)}")
        
#         response = templates.TemplateResponse(
#             "index.html",
#             {"request": request}
#         )
#         logger.info("Successfully rendered index.html template")
#         return response
        
#     except Exception as e:
#         logger.error(f"Error in app_entry: {e}", exc_info=True)
#         logger.error(f"Template directory: webapp/templates")
#         logger.error(f"Looking for: index.html")
#         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """Profile page for Mini App."""
    try:
        return templates.TemplateResponse(
            "profile.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering profile page: {e}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Ошибка загрузки профиля"}
        )


@app.get("/loyalty-history", response_class=HTMLResponse)
async def loyalty_history_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """Loyalty history page for Mini App."""
    try:
        return templates.TemplateResponse(
            "loyalty_history.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering loyalty history page: {e}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Ошибка загрузки истории баллов"}
        )


@app.get("/referral-stats", response_class=HTMLResponse)
async def referral_stats_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """Referral statistics page for Mini App."""
    try:
        return templates.TemplateResponse(
            "referral_stats.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering referral stats page: {e}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Ошибка загрузки реферальной статистики"}
        )


@app.get("/order-history", response_class=HTMLResponse)
async def order_history_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """Order history page for Mini App."""
    try:
        return templates.TemplateResponse(
            "order_history.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering order history page: {e}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Ошибка загрузки истории заказов"}
        )


@app.get("/loyalty-levels", response_class=HTMLResponse)
async def loyalty_levels_page(
    request: Request,
    db: AsyncSession = Depends(get_db),
    telegram_user: dict = Depends(get_current_telegram_user)
):
    """Loyalty levels page for Mini App."""
    try:
        return templates.TemplateResponse(
            "loyalty_levels.html",
            {"request": request}
        )
    except Exception as e:
        logger.error(f"Error rendering loyalty levels page: {e}")
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "Ошибка загрузки уровней лояльности"}
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "webapp.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )
