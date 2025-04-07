import logging

from datetime import date, timedelta

from typing import Sequence

from sqlalchemy import select, or_, extract, and_

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact
from src.schemas.contacts import BaseContact, UpdateContact

logger = logging.getLogger("uvicorn.error")


class ContactsRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, limit: int, offset: int) -> Sequence[Contact]:
        """
        Get a list of contacts from the database with pagination.

        :param limit: The maximum number of contacts to return.
        :param offset: The number of contacts to skip before starting to collect the result set.
        :return: A list of contacts.
        """
        query = select(Contact).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        """
        Get a contact by ID.

        :param contact_id: The ID of the contact to retrieve.
        :return: The contact if found, None otherwise.
        """
        query = select(Contact).filter_by(id=contact_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_contact(self, body: BaseContact) -> Contact:
        """
        Create a new contact in the database.

        :param contact: The contact to create.
        :return: The created contact.
        """
        new_contact = Contact(**body.model_dump())
        self.db.add(new_contact)
        await self.db.commit()
        await self.db.refresh(new_contact)
        return new_contact

    async def update_contact(
        self, contact_id: int, body: UpdateContact
    ) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            update_data = body.model_dump(exclude_unset=True)

            for key, value in update_data.items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        """
        Remove a contact from the database.

        :param contact_id: The ID of the contact to remove.
        """
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def search_contacts(
        self, query: str, limit: int = 10, offset: int = 0
    ) -> Sequence[Contact]:
        """
        Search for contacts by first name, last name, email, or phone.

        :param search: The search term.
        :param limit: The maximum number of contacts to return.
        :param offset: The number of contacts to skip before starting to collect the result set.
        :return: A list of matching contacts.
        """
        query = (
            select(Contact)
            .where(
                or_(
                    Contact.first_name.ilike(f"%{query}%"),
                    Contact.last_name.ilike(f"%{query}%"),
                    Contact.email.ilike(f"%{query}%"),
                    Contact.phone.ilike(f"%{query}%"),
                )
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_upcoming_birthdays(self, days_ahead: int = 7) -> Sequence[Contact]:
        today = date.today()
        upcoming_birthday = today + timedelta(days=days_ahead)

        query = select(Contact).where(
            or_(
                and_(
                    extract("month", Contact.birthday) == today.month,
                    extract("day", Contact.birthday) >= today.day,
                ),
                and_(
                    extract("month", Contact.birthday) == upcoming_birthday.month,
                    extract("day", Contact.birthday) <= upcoming_birthday.day,
                ),
                and_(
                    extract("month", Contact.birthday) > today.month,
                    extract("month", Contact.birthday) < upcoming_birthday.month,
                ),
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()
