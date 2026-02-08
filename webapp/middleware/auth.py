# middleware/auth.py
from fastapi import Request, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# from shared.services.jwt import decode_access_token
from shared.services.cache_service import get_session, CacheUser
from shared.logging_config import get_logger

logger = get_logger(__name__)


from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException

import logging


logger = logging.getLogger(__name__)



class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # skip non-api
        if not path.startswith("/api/"):
            return await call_next(request)

        # whitelist
        if path in ("/api/auth/user", "/health"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return self._error(
                status=401,
                error="unauthorized",
                message="Authorization header is missing",
            )

        try:
            scheme, token = auth_header.split(" ", 1)
        except ValueError:
            return self._error(
                status=401,
                error="unauthorized",
                message="Invalid authorization header format",
            )

        scheme = scheme.lower()

        if scheme == "bearer":
            session = await get_session(token)
            role = "user"

        elif scheme == "TMA":
            session = await get_tma_session(token)
            role = "tma"

        elif scheme == "iikofront":
            session = await get_admin_session(token)
            role = "admin"

        else:
            return self._error(
                status=401,
                error="unauthorized",
                message=f"Unsupported auth scheme: {scheme}",
            )

        if not session:
            return self._error(
                status=401,
                error="unauthorized",
                message="Invalid or expired token",
            )

        # кладём в state всё, что может понадобиться дальше
        request.state.user = session
        request.state.auth_scheme = scheme
        request.state.role = role

        return await call_next(request)

    @staticmethod
    def _error(status: int, error: str, message: str):
        return JSONResponse(
            status_code=status,
            content={
                "error": error,
                "message": message,
            },
        )


# class AuthMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request: Request, call_next):
#         path = request.url.path

#         # skip non-api
#         if not path.startswith("/api/"):
#             return await call_next(request)

#         # whitelist
#         if path in ("/api/auth", "/health"):
#             return await call_next(request)

#         auth = request.headers.get("Authorization")
#         if not auth or not auth.startswith("Bearer "):
#             return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

#         token = auth[7:]
#         session = await get_session(token)

#         if not session:
#             return JSONResponse(status_code=401, content={"detail": "Not valid token"})

#         request.state.user = session
#         return await call_next(request)




def get_current_telegram_user(request: Request) -> CacheUser:
    user = getattr(request.state, "user", None)
    if user is None:
        # на случай если middleware не отработал
        raise HTTPException(401, "Unauthorized")
    return user


# class JWTAuthMiddleware(BaseHTTPMiddleware):

#     async def dispatch(self, request: Request, call_next):
#         try:
#             # HTML и статика — без auth
#             # if not request.url.path.startswith("/api/"):
#             #     logger.debug(f"Middleware: Skipping auth for non-API path: {request.url.path}")
#             #     return await call_next(request)

#             # auth endpoint и health — без JWT
#             if request.url.path in ["/api/auth", "/health"]:
#                 logger.debug(f"Middleware: Skipping auth for whitelisted path: {request.url.path}")
#                 return await call_next(request)

#             logger.debug(f"Middleware: Checking auth for API path: {request.url.path}")
            
#             auth = request.headers.get("Authorization")
#             if not auth or not auth.startswith("Bearer "):
#                 logger.warning(f"Middleware: No valid Authorization header for {request.url.path}")
#                 raise HTTPException(401, "Unauthorized")
            
#             token = auth[7:]
#             #JWT
#             payload = decode_access_token(token)

#             if not payload:
#                 logger.warning(f"Middleware: Invalid token for {request.url.path}")
#                 raise HTTPException(401, "Invalid token")

#             request.state.user = payload
#             logger.debug(f"Middleware: Auth successful for user {payload.get('id', 'unknown')}")
#             return await call_next(request)
            
#         except HTTPException:
#             raise
#         except Exception as e:
#             logger.error(f"Middleware error for {request.url.path}: {e}", exc_info=True)
#             raise HTTPException(500, "Internal server error")