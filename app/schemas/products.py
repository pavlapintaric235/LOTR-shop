from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.categories import CategoryRead


class ProductCreate(BaseModel):
    slug: str = Field(min_length=3, max_length=100)
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(max_length=255)
    price: Decimal = Field(gt=0)
    stock: int = Field(default=0, ge=0)
    image_url: str = Field(max_length=255)
    is_featured: bool = Field(default=False)
    category_id: int


class ProductUpdate(BaseModel):
    slug: str | None = Field(min_length=3, max_length=100)
    name: str | None = Field(min_length=3, max_length=100)
    description: str | None = Field(max_length=255)
    price: Decimal | None = Field(gt=0)
    stock: int | None = Field(default=None, ge=0)
    image_url: str | None = Field(max_length=255)
    is_featured: bool | None = Field(default=None)
    category_id: int | None = Field(default=None)


class ProductRead(BaseModel):
    id: int
    slug: str
    name: str
    description: str
    price: Decimal
    stock: int
    image_url: str
    is_featured: bool
    category: CategoryRead

    model_config = {"from_attributes": True}


class HomepageRead(BaseModel):
    featured_products: list[ProductRead]
    most_wanted_products: list[ProductRead]