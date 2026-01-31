from fastapi import Request, HTTPException
from shared.services.cache_service import CacheUser

def get_current_user(request: Request) -> CacheUser:
    user = getattr(request.state, "user", None)
    if user is None:
        # на случай если middleware не отработал
        raise HTTPException(401, "Unauthorized")
    return user