from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional

class Item(BaseModel):
    name: str = Field(..., example="Iron Sword")
    type: str = Field(..., example="Weapon")
    value: int = Field(..., gt=0, example=100)
    effect_value: Optional[int] = Field(None, example=15) 

class Stats(BaseModel):
    strength: int = Field(10, ge=1, le=20) 
    dexterity: int = Field(10, ge=1, le=20)
    intelligence: int = Field(10, ge=1, le=20)
    hp_current: int = Field(20)
    hp_max: int = Field(20)

class Character(BaseModel):
    name: str = Field(..., min_length=2, example="Aragorn")
    character_class: str = Field(..., example="Warrior")
    level: int = Field(1, ge=1, example=1) 
    stats: Stats 
    inventory: List[Item] = [] 
    campaign_id: Optional[str] = None
    user_id: Optional[str] = None

class Campaign(BaseModel):
    title: str = Field(..., example="The Dark Tower")
    description: Optional[str] = None
    game_master_id: str 


class User(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr 