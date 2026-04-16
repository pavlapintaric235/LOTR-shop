from pydantic import BaseModel, Field

class CategoryCreate(BaseModel):
    slug: str = Field(min_length=3, max_length=100)
    name: str = Field(min_length=3, max_length=100)


class CategoryRead(BaseModel):
    id: int
    slug: str
    name: str

    model_config = {"from_attributes": True}