import asyncio
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from typing import Annotated, Optional
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.admin.views import BookingsAdmin, UsersAdmin, RoomsAdmin, HotelsAdmin
from app.database import engine
from app.users.model import Users
from app.bookings.router import router as router_bookings
from app.config import settings
from app.users.router import router as router_users #,router_auth доработка функционала 1.8
from app.hotels.router import router as router_hotels        
from app.pages.router import router as router_pages

from app.images.router import router as router_images

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

from sqladmin import Admin, ModelView
from app.admin.auth import authentication_backend

app = FastAPI()

# import logging       

async def get_data():
    data = await asyncio.sleep(3) # имитация данных необходимых для старта приложения 
    
async def get_cache():
    while True:
        await get_data()
        await asyncio.sleep(60*5)  # имитация кода, наполняющего справочные данные или набирание кэша, бесконечная функция 

# при запуске 
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}") 
    FastAPICache.init(RedisBackend(redis), prefix="cache") #prefix="fastapi-cache" изначально
    # await get_data()
    # asyncio.create_task(get_cache()) # бесконечная задача
    yield
# при выключении (на данный моент этот кусок кода еще не написан)

app = FastAPI(lifespan=lifespan)  # lifespan также нужно будет передатьь в VersionedFastAPI

'''Ниже закомментирован более новый способ  '''

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)
    
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     logger.info("Service started")
#     yield
#     logger.info("Service exited")

#app = FastAPI(lifespan=lifespan)


app.mount("/static", StaticFiles(directory="app/static"), "static")

#app.include_router(router_auth)                          доработка функционала
app.include_router(router_users)
app.include_router(router_hotels)        
app.include_router(router_bookings)

app.include_router(router_pages)

app.include_router(router_images)


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type", 
        "Set-Cookie", 
        "Access-Control-Allow-Headers", 
        "Access-Control-Allow-Origin", 
        "Authorization"
    ],
)


admin = Admin(
    app=app,
    engine=engine,
    authentication_backend=authentication_backend)  


    
admin.add_view(UsersAdmin)
admin.add_view(BookingsAdmin)
admin.add_view(RoomsAdmin)
admin.add_view(HotelsAdmin)



# class SHotel(BaseModel):
#     adress: str
#     name: str
#     stars: int
    

@app.get('/hotels') #,response_model=list[SHotel])
def get_hotels(
    location: str,
    date_from: date,
    date_to: date,
    has_spa: Annotated[bool | None, Query()] = None,         
    stars: Annotated[int | None, Query(ge=1,le=5)] = None 
):
    hotels = [
            {
                'adress': 'Altai',
                'name': 'SuperHotel',
                "stars": 5,
               }
              ]
    return hotels





















# class SBooking(BaseModel):
#     room_id: int
#     date_from: date
#     date_to: date

# @app.post('/bookings')
# def add_booking(booking: SBooking):
#     pass

# С версии 0.95.0 рекомендуется использовать именно Annotated. Вот пример: 
# stars: Annotated[int | None, Query(ge=1, le=5)] = None
# К сожалению Swagger UI не поддерживает int | None в таком случае, 
# и мы будем видеть просто что это query param (без типа integer, minimum и maximum). 
# Это проблема именно Swagger UI (он просто не поддерживает эту фичу OpenAPI спецификации), но зато ReDoc поддерживает. 
# Так что рекомендую смотреть именно на ReDoc (на самом деле крутой инструмент, 
# просто в отличии от Swagger UI он не позволяет отправлять запросы).



# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# async def root():
#     return {"message": "Привет, мир"}
