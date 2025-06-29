from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: UUID = Field(alias="sub")
    
    model_config = ConfigDict(
        populate_by_name=True,
    ) 