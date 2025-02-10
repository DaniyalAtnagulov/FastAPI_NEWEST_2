from datetime import date

from pydantic import BaseModel

class SHotelInfo(BaseModel):
    id: int
    name: str
    location: str
    services: list[str]
    rooms_quantity: int
    image_id: int
    
    # class Config():
    #     orm_mode = True  