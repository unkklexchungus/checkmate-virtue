"""
Structured error responses for inspection module.
Follows problem+json style and provides consistent error formatting.
"""

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from datetime import datetime
import traceback
import sys


class InspectionError(Exception):
    """Base exception for inspection-related errors."""
    
    def __init__(
        self,
        title: str,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        instance: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        self.title = title
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        self.instance = instance
        self.additional_data = additional_data or {}
        super().__init__(detail)


class ValidationError(InspectionError):
    """Validation error with field-specific details."""
    
    def __init__(
        self,
        detail: str,
        field_errors: Optional[List[Dict[str, Any]]] = None,
        instance: Optional[str] = None
    ):
        super().__init__(
            title="Validation Error",
            detail=detail,
            status_code=422,
            error_code="VALIDATION_ERROR",
            instance=instance,
            additional_data={"field_errors": field_errors or []}
        )


class NotFoundError(InspectionError):
    """Resource not found error."""
    
    def __init__(self, resource_type: str, resource_id: str, instance: Optional[str] = None):
        super().__init__(
            title="Resource Not Found",
            detail=f"{resource_type} with ID '{resource_id}' not found",
            status_code=404,
            error_code="NOT_FOUND",
            instance=instance
        )


class ConflictError(InspectionError):
    """Resource conflict error."""
    
    def __init__(self, detail: str, instance: Optional[str] = None):
        super().__init__(
            title="Conflict",
            detail=detail,
            status_code=409,
            error_code="CONFLICT",
            instance=instance
        )


class ServiceError(InspectionError):
    """Service-level error."""
    
    def __init__(self, detail: str, service: str, instance: Optional[str] = None):
        super().__init__(
            title="Service Error",
            detail=detail,
            status_code=503,
            error_code="SERVICE_ERROR",
            instance=instance,
            additional_data={"service": service}
        )


def create_problem_response(
    error: InspectionError,
    request_path: Optional[str] = None,
    include_traceback: bool = False
) -> JSONResponse:
    """
    Create a problem+json style response.
    
    Args:
        error: The inspection error
        request_path: The request path for the instance field
        include_traceback: Whether to include stack trace (dev only)
    
    Returns:
        JSONResponse with problem+json format
    """
    problem_data = {
        "type": f"https://api.checkmate-virtue.com/errors/{error.error_code.lower()}" if error.error_code else "about:blank",
        "title": error.title,
        "detail": error.detail,
        "status": error.status_code,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if error.instance or request_path:
        problem_data["instance"] = error.instance or request_path
    
    if error.error_code:
        problem_data["error_code"] = error.error_code
    
    if error.additional_data:
        problem_data.update(error.additional_data)
    
    if include_traceback:
        problem_data["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=error.status_code,
        content=problem_data,
        headers={
            "Content-Type": "application/problem+json"
        }
    )


def create_validation_response(
    field_errors: List[Dict[str, Any]],
    detail: str = "Validation failed",
    request_path: Optional[str] = None
) -> JSONResponse:
    """
    Create a validation error response.
    
    Args:
        field_errors: List of field-specific validation errors
        detail: General validation message
        request_path: The request path for the instance field
    
    Returns:
        JSONResponse with validation error details
    """
    return create_problem_response(
        ValidationError(detail, field_errors, request_path),
        request_path
    )


def create_not_found_response(
    resource_type: str,
    resource_id: str,
    request_path: Optional[str] = None
) -> JSONResponse:
    """
    Create a not found error response.
    
    Args:
        resource_type: Type of resource (e.g., "Inspection", "Vehicle")
        resource_id: ID of the resource that wasn't found
        request_path: The request path for the instance field
    
    Returns:
        JSONResponse with not found error details
    """
    return create_problem_response(
        NotFoundError(resource_type, resource_id, request_path),
        request_path
    )


def create_conflict_response(
    detail: str,
    request_path: Optional[str] = None
) -> JSONResponse:
    """
    Create a conflict error response.
    
    Args:
        detail: Conflict description
        request_path: The request path for the instance field
    
    Returns:
        JSONResponse with conflict error details
    """
    return create_problem_response(
        ConflictError(detail, request_path),
        request_path
    )


def create_service_error_response(
    detail: str,
    service: str,
    request_path: Optional[str] = None,
    include_traceback: bool = False
) -> JSONResponse:
    """
    Create a service error response.
    
    Args:
        detail: Service error description
        service: Name of the service that failed
        request_path: The request path for the instance field
        include_traceback: Whether to include stack trace (dev only)
    
    Returns:
        JSONResponse with service error details
    """
    return create_problem_response(
        ServiceError(detail, service, request_path),
        request_path,
        include_traceback
    )


def handle_inspection_error(
    error: Exception,
    request_path: Optional[str] = None,
    include_traceback: bool = False
) -> JSONResponse:
    """
    Handle inspection errors and convert to appropriate responses.
    
    Args:
        error: The exception that occurred
        request_path: The request path for the instance field
        include_traceback: Whether to include stack trace (dev only)
    
    Returns:
        JSONResponse with appropriate error details
    """
    if isinstance(error, InspectionError):
        return create_problem_response(error, request_path, include_traceback)
    
    # Handle other exceptions
    if isinstance(error, HTTPException):
        return create_problem_response(
            InspectionError(
                title="HTTP Error",
                detail=error.detail,
                status_code=error.status_code,
                error_code=f"HTTP_{error.status_code}",
                instance=request_path
            ),
            request_path
        )
    
    # Handle unexpected errors
    return create_problem_response(
        InspectionError(
            title="Internal Server Error",
            detail="An unexpected error occurred",
            status_code=500,
            error_code="INTERNAL_ERROR",
            instance=request_path
        ),
        request_path,
        include_traceback
    )


# Convenience functions for common error scenarios
def inspection_not_found(inspection_id: str, request_path: Optional[str] = None) -> JSONResponse:
    """Create response for inspection not found."""
    return create_not_found_response("Inspection", inspection_id, request_path)


def vehicle_not_found(vehicle_id: str, request_path: Optional[str] = None) -> JSONResponse:
    """Create response for vehicle not found."""
    return create_not_found_response("Vehicle", vehicle_id, request_path)


def vin_decode_failed(vin: str, reason: str, request_path: Optional[str] = None) -> JSONResponse:
    """Create response for VIN decode failure."""
    return create_service_error_response(
        f"Failed to decode VIN '{vin}': {reason}",
        "VIN Decoder Service",
        request_path
    )


def file_upload_failed(filename: str, reason: str, request_path: Optional[str] = None) -> JSONResponse:
    """Create response for file upload failure."""
    return create_problem_response(
        InspectionError(
            title="File Upload Failed",
            detail=f"Failed to upload file '{filename}': {reason}",
            status_code=400,
            error_code="FILE_UPLOAD_ERROR",
            instance=request_path
        ),
        request_path
    )


def template_not_found(template_name: str, request_path: Optional[str] = None) -> JSONResponse:
    """Create response for template not found."""
    return create_not_found_response("Template", template_name, request_path)
