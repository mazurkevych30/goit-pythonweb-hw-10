from sqlalchemy.ext.asyncio import AsyncSession
from src.repositories.contacts_repository import ContactsRepository

from src.schemas.contacts import BaseContact, UpdateContact


class ContactsService:
    def __init__(self, db: AsyncSession):
        self.contacts_repository = ContactsRepository(db)

    async def create_contact(self, body: BaseContact):
        return await self.contacts_repository.create_contact(body)

    async def get_contacts(self, limit: int, offset: int):
        return await self.contacts_repository.get_contacts(limit, offset)

    async def ge_contact_by_id(self, contact_id: int):
        return await self.contacts_repository.get_contact_by_id(contact_id)

    async def update_contact(self, contact_id: int, body: UpdateContact):
        return await self.contacts_repository.update_contact(contact_id, body)

    async def remove_contact(self, contact_id: int):
        return await self.contacts_repository.remove_contact(contact_id)

    async def search_contacts(self, query: str, limit: int, offset: int):
        return await self.contacts_repository.search_contacts(
            query=query, limit=limit, offset=offset
        )

    async def get_upcoming_birthdays(self, days_ahead: int):
        return await self.contacts_repository.get_upcoming_birthdays(days_ahead)
