import asyncio
from datetime import datetime
import json
import pytest
from sqlalchemy import insert
from app.config import settings
from app.database import Base, async_session_maker, engine

from app.bookings.model import Bookings 
from app.hotels. model import Hotels
from app.hotels.rooms.model import Rooms
from app.users.model import Users

from app.main import app as fastapi_app

from fastapi.testclient import TestClient
from httpx import AsyncClient
from httpx import ASGITransport


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    def open_mock_json(model: str):
        with open(f"app/tests/mock_{model}.json", "r", encoding="utf-8") as file:
            return json.load(file)
            
    hotels = open_mock_json("hotels")
    rooms = open_mock_json("rooms")
    users = open_mock_json("users")
    bookings = open_mock_json("bookings")
    
    for booking in bookings:
        booking["date_from"] = datetime.strptime(booking["date_from"], "%Y-%m-%d").date()
        booking["date_to"] = datetime.strptime(booking["date_to"], "%Y-%m-%d").date()
    
    async with async_session_maker() as session:
        add_hotels = insert(Hotels).values(hotels)
        add_rooms = insert(Rooms).values(rooms) 
        add_users = insert(Users).values(users)
        add_bookings = insert(Bookings).values(bookings)
        
        await session.execute(add_hotels)
        await session.execute(add_rooms)
        await session.execute(add_users)
        await session.execute(add_bookings)
        
        await session.commit()
        
@pytest.fixture(scope="session")
def event_loop():
    """Создает и корректно закрывает event loop для всех тестов в сессии."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.run_until_complete(loop.shutdown_asyncgens())  # Закрываем генераторы
    loop.close()
    
    """Стоит отметить, что pytest-asyncio больше не рекомендует переопределять event_loop вручную, просему можно поисать другие способы его реализации
    Лучший вариант – удалить event_loop и заменить его на anyio_backend в conftest.py. 
    @pytest.fixture(scope="session")
    def anyio_backend():
        return "asyncio"
    Если event_loop нужен, убедитесь, что он корректно закрывает ресурсы.""" 

@pytest.fixture(scope="function")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as ac:
        yield ac
        
@pytest.fixture(scope="function")
async def session():
    async with async_session_maker() as session:
        yield session
            
        
            
    
     

