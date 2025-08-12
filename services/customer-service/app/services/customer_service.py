"""
Customer service business logic.
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import select, and_, or_
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status

from app.models.customer import Customer, Address, ContactInfo
from app.schemas.customer import CustomerCreate, CustomerUpdate, AddressCreate, ContactInfoCreate


class CustomerService:
    """Customer service."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_customer(self, customer_data: CustomerCreate) -> Customer:
        """Create a new customer."""
        # Create address if provided
        address = None
        if customer_data.address:
            address = Address(**customer_data.address.model_dump())
            self.session.add(address)
            await self.session.flush()
        
        # Create contact info if provided
        contact = None
        if customer_data.contact:
            contact = ContactInfo(**customer_data.contact.model_dump())
            self.session.add(contact)
            await self.session.flush()
        
        # Create customer
        customer = Customer(
            name=customer_data.name,
            company=customer_data.company,
            tax_id=customer_data.tax_id,
            notes=customer_data.notes,
            address_id=address.id if address else None,
            contact_id=contact.id if contact else None
        )
        
        self.session.add(customer)
        await self.session.commit()
        await self.session.refresh(customer)
        
        return customer
    
    async def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID."""
        return await self.session.exec(
            select(Customer)
            .where(Customer.id == customer_id)
        ).first()
    
    async def get_customers(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Customer]:
        """Get customers with optional search."""
        query = select(Customer)
        
        if search:
            query = query.where(
                or_(
                    Customer.name.contains(search),
                    Customer.company.contains(search),
                    Customer.tax_id.contains(search)
                )
            )
        
        return await self.session.exec(
            query.offset(skip).limit(limit)
        ).all()
    
    async def update_customer(self, customer_id: int, customer_data: CustomerUpdate) -> Optional[Customer]:
        """Update customer."""
        customer = await self.get_customer_by_id(customer_id)
        if not customer:
            return None
        
        # Update customer fields
        update_data = customer_data.model_dump(exclude_unset=True, exclude={"address", "contact"})
        for field, value in update_data.items():
            setattr(customer, field, value)
        
        # Update address if provided
        if customer_data.address:
            if customer.address_id:
                # Update existing address
                address = await self.session.exec(
                    select(Address).where(Address.id == customer.address_id)
                ).first()
                if address:
                    address_data = customer_data.address.model_dump(exclude_unset=True)
                    for field, value in address_data.items():
                        setattr(address, field, value)
            else:
                # Create new address
                address = Address(**customer_data.address.model_dump())
                self.session.add(address)
                await self.session.flush()
                customer.address_id = address.id
        
        # Update contact info if provided
        if customer_data.contact:
            if customer.contact_id:
                # Update existing contact
                contact = await self.session.exec(
                    select(ContactInfo).where(ContactInfo.id == customer.contact_id)
                ).first()
                if contact:
                    contact_data = customer_data.contact.model_dump(exclude_unset=True)
                    for field, value in contact_data.items():
                        setattr(contact, field, value)
            else:
                # Create new contact
                contact = ContactInfo(**customer_data.contact.model_dump())
                self.session.add(contact)
                await self.session.flush()
                customer.contact_id = contact.id
        
        customer.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(customer)
        
        return customer
    
    async def delete_customer(self, customer_id: int) -> bool:
        """Delete customer."""
        customer = await self.get_customer_by_id(customer_id)
        if not customer:
            return False
        
        await self.session.delete(customer)
        await self.session.commit()
        return True
    
    async def count_customers(self, search: Optional[str] = None) -> int:
        """Count customers with optional search."""
        query = select(Customer)
        
        if search:
            query = query.where(
                or_(
                    Customer.name.contains(search),
                    Customer.company.contains(search),
                    Customer.tax_id.contains(search)
                )
            )
        
        result = await self.session.exec(query)
        return len(result.all())
