"""Error handlers for FastAPI application."""
import asyncio
import traceback
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import (
    SQLAlchemyError, 
    IntegrityError, 
    OperationalError,
    DisconnectionError
)
from pydantic import ValidationError

from shared.logging_config import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base application error."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize application error."""
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AppError):
    """Validation error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(AppError):
    """Resource not found error."""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            message=f"{resource} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)}
        )


class AuthenticationError(AppError):
    """Authentication error."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(AppError):
    """Authorization error."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )


class BusinessLogicError(AppError):
    """Business logic error."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )


class DatabaseError(AppError):
    """Database operation error."""
    
    def __init__(self, message: str = "Database operation failed", original_error: Optional[Exception] = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
            
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class ExternalServiceError(AppError):
    """External service error."""
    
    def __init__(self, service: str, message: str = "External service unavailable"):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


async def retry_database_operation(operation, max_retries: int = 3, delay: float = 1.0):
    """
    Retry database operation with exponential backoff.
    
    Args:
        operation: Async function to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        
    Returns:
        Result of the operation
        
    Raises:
        DatabaseError: If all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await operation()
        except (OperationalError, DisconnectionError) as e:
            last_exception = e
            if attempt < max_retries:
                wait_time = delay * (2 ** attempt)  # Exponential backoff
                logger.warning(
                    f"Database operation failed (attempt {attempt + 1}/{max_retries + 1}), "
                    f"retrying in {wait_time}s: {e}"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Database operation failed after {max_retries + 1} attempts: {e}")
        except Exception as e:
            # Don't retry for other types of errors
            logger.error(f"Database operation failed with non-retryable error: {e}")
            raise DatabaseError("Database operation failed", e)
    
    # If we get here, all retries failed
    raise DatabaseError("Database operation failed after retries", last_exception)


def create_error_response(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """
    Create standardized error response.
    
    Args:
        status_code: HTTP status code
        message: Error message
        error_code: Application-specific error code
        details: Additional error details
        request_id: Request ID for tracking
        
    Returns:
        JSONResponse with error details
    """
    error_response = {
        "error": {
            "message": message,
            "code": error_code or "UNKNOWN_ERROR",
            "status_code": status_code
        }
    }
    
    if details:
        error_response["error"]["details"] = details
    
    if request_id:
        error_response["error"]["request_id"] = request_id
    
    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


def setup_error_handlers(app: FastAPI) -> None:
    """Setup error handlers for FastAPI application."""
    
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        """Handle application-specific errors."""
        logger.error(
            f"Application error: {exc.message} (code: {exc.error_code}, status: {exc.status_code})",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return create_error_response(
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.details
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Handle HTTP exceptions."""
        logger.warning(
            f"HTTP exception: {exc.detail} (status: {exc.status_code})",
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return create_error_response(
            status_code=exc.status_code,
            message=exc.detail,
            error_code="HTTP_ERROR"
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle request validation errors."""
        logger.warning(
            f"Validation error: {exc.errors()}",
            extra={
                "errors": exc.errors(),
                "path": request.url.path,
                "method": request.method
            }
        )
        
        # Format validation errors for user-friendly response
        formatted_errors = []
        for error in exc.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            formatted_errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            details={"errors": formatted_errors}
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Handle Pydantic validation errors."""
        logger.warning(
            f"Pydantic validation error: {exc.errors()}",
            extra={
                "errors": exc.errors(),
                "path": request.url.path,
                "method": request.method
            }
        )
        
        return create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Data validation failed",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()}
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Handle SQLAlchemy database errors."""
        logger.error(
            f"Database error: {str(exc)}",
            extra={
                "error_type": type(exc).__name__,
                "path": request.url.path,
                "method": request.method
            },
            exc_info=True
        )
        
        # Handle specific database errors
        if isinstance(exc, IntegrityError):
            return create_error_response(
                status_code=status.HTTP_409_CONFLICT,
                message="Data integrity constraint violation",
                error_code="INTEGRITY_ERROR"
            )
        elif isinstance(exc, (OperationalError, DisconnectionError)):
            return create_error_response(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                message="Database temporarily unavailable",
                error_code="DATABASE_UNAVAILABLE"
            )
        else:
            return create_error_response(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Database operation failed",
                error_code="DATABASE_ERROR"
            )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle all other exceptions."""
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "error_type": type(exc).__name__,
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        return create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_code="INTERNAL_ERROR"
        )


# Utility functions for common error scenarios
def raise_not_found(resource: str, identifier: Any) -> None:
    """Raise a not found error."""
    raise NotFoundError(resource, identifier)


def raise_validation_error(message: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Raise a validation error."""
    raise ValidationError(message, details)


def raise_business_logic_error(message: str, details: Optional[Dict[str, Any]] = None) -> None:
    """Raise a business logic error."""
    raise BusinessLogicError(message, details)


def raise_authentication_error(message: str = "Authentication failed") -> None:
    """Raise an authentication error."""
    raise AuthenticationError(message)


def raise_authorization_error(message: str = "Access denied") -> None:
    """Raise an authorization error."""
    raise AuthorizationError(message)