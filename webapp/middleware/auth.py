from fastapi import Request, HTTPException, Depends
from starlette.middleware.base import BaseHTTPMiddleware

from shared.services.jwt import decode_access_token
from shared.logging_config import get_logger

logger = get_logger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        try:
            # HTML и статика — без auth
            if not request.url.path.startswith("/api/"):
                logger.debug(f"Middleware: Skipping auth for non-API path: {request.url.path}")
                return await call_next(request)

            # auth endpoint и health — без JWT
            if request.url.path in ["/api/auth", "/health"]:
                logger.debug(f"Middleware: Skipping auth for whitelisted path: {request.url.path}")
                return await call_next(request)

            logger.debug(f"Middleware: Checking auth for API path: {request.url.path}")
            
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                logger.warning(f"Middleware: No valid Authorization header for {request.url.path}")
                raise HTTPException(401, "Unauthorized")

            token = auth[7:]
            payload = decode_access_token(token)

            if not payload:
                logger.warning(f"Middleware: Invalid token for {request.url.path}")
                raise HTTPException(401, "Invalid token")

            request.state.user = payload
            logger.debug(f"Middleware: Auth successful for user {payload.get('id', 'unknown')}")
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Middleware error for {request.url.path}: {e}", exc_info=True)
            raise HTTPException(500, "Internal server error")


def get_current_telegram_user(request: Request) -> dict:
    """Get current telegram user from request state."""
    try:
        if not hasattr(request.state, 'user'):
            logger.warning("No user in request state - unauthorized access attempt")
            raise HTTPException(401, "Unauthorized")
        
        user = request.state.user
        logger.debug(f"Retrieved user from state: {user.get('id', 'unknown')}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}", exc_info=True)
        raise HTTPException(500, "Internal server error")
