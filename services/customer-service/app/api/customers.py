"""
Customer API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession


from _shared.models.base import BaseResponse, PaginationParams
from app.db.session import get_session
from app.models.customer import Customer, Address, ContactInfo
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse,
    CustomerDetailResponse, CustomerPaginatedResponse, AddressResponse, ContactInfoResponse
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/v1/customers", tags=["Customers"])


@router.post("/", response_model=CustomerDetailResponse)
async def create_customer(
    customer_data: CustomerCreate,
    session: AsyncSession = Depends(get_session)
):
    """Create a new customer."""
    customer_service = CustomerService(session)
    customer = await customer_service.create_customer(customer_data)
    
    return CustomerDetailResponse(
        message="Customer created successfully",
        data=CustomerResponse(
            id=customer.id,
            name=customer.name,
            company=customer.company,
            tax_id=customer.tax_id,
            notes=customer.notes,
            full_name=customer.full_name,
            address=AddressResponse(
                id=customer.address.id,
                street=customer.address.street,
                city=customer.address.city,
                state=customer.address.state,
                zip_code=customer.address.zip_code,
                country=customer.address.country
            ) if customer.address else None,
            contact=ContactInfoResponse(
                id=customer.contact.id,
                phone=customer.contact.phone,
                email=customer.contact.email,
                website=customer.contact.website
            ) if customer.contact else None,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        )
    )


@router.get("/", response_model=CustomerPaginatedResponse)
async def list_customers(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
    session: AsyncSession = Depends(get_session)
):
    """List customers with pagination."""
    customer_service = CustomerService(session)
    
    skip = (page - 1) * size
    customers = await customer_service.get_customers(skip=skip, limit=size, search=search)
    total = await customer_service.count_customers(search=search)
    
    customer_responses = []
    for customer in customers:
        customer_responses.append(CustomerResponse(
            id=customer.id,
            name=customer.name,
            company=customer.company,
            tax_id=customer.tax_id,
            notes=customer.notes,
            full_name=customer.full_name,
            address=AddressResponse(
                id=customer.address.id,
                street=customer.address.street,
                city=customer.address.city,
                state=customer.address.state,
                zip_code=customer.address.zip_code,
                country=customer.address.country
            ) if customer.address else None,
            contact=ContactInfoResponse(
                id=customer.contact.id,
                phone=customer.contact.phone,
                email=customer.contact.email,
                website=customer.contact.website
            ) if customer.contact else None,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        ))
    
    pages = (total + size - 1) // size
    
    return CustomerPaginatedResponse(
        items=customer_responses,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Get customer by ID."""
    customer_service = CustomerService(session)
    customer = await customer_service.get_customer_by_id(customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerDetailResponse(
        data=CustomerResponse(
            id=customer.id,
            name=customer.name,
            company=customer.company,
            tax_id=customer.tax_id,
            notes=customer.notes,
            full_name=customer.full_name,
            address=AddressResponse(
                id=customer.address.id,
                street=customer.address.street,
                city=customer.address.city,
                state=customer.address.state,
                zip_code=customer.address.zip_code,
                country=customer.address.country
            ) if customer.address else None,
            contact=ContactInfoResponse(
                id=customer.contact.id,
                phone=customer.contact.phone,
                email=customer.contact.email,
                website=customer.contact.website
            ) if customer.contact else None,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        )
    )


@router.put("/{customer_id}", response_model=CustomerDetailResponse)
async def update_customer(
    customer_id: int,
    customer_data: CustomerUpdate,
    session: AsyncSession = Depends(get_session)
):
    """Update customer."""
    customer_service = CustomerService(session)
    customer = await customer_service.update_customer(customer_id, customer_data)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return CustomerDetailResponse(
        message="Customer updated successfully",
        data=CustomerResponse(
            id=customer.id,
            name=customer.name,
            company=customer.company,
            tax_id=customer.tax_id,
            notes=customer.notes,
            full_name=customer.full_name,
            address=AddressResponse(
                id=customer.address.id,
                street=customer.address.street,
                city=customer.address.city,
                state=customer.address.state,
                zip_code=customer.address.zip_code,
                country=customer.address.country
            ) if customer.address else None,
            contact=ContactInfoResponse(
                id=customer.contact.id,
                phone=customer.contact.phone,
                email=customer.contact.email,
                website=customer.contact.website
            ) if customer.contact else None,
            created_at=customer.created_at,
            updated_at=customer.updated_at
        )
    )


@router.delete("/{customer_id}", response_model=BaseResponse)
async def delete_customer(
    customer_id: int,
    session: AsyncSession = Depends(get_session)
):
    """Delete customer."""
    customer_service = CustomerService(session)
    success = await customer_service.delete_customer(customer_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return BaseResponse(message="Customer deleted successfully")
