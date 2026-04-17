from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text # type: ignore
from sqlalchemy.orm import Mapped, mapped_column, relationship #type: ignore

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.category import Category
    from app.models.order_item import OrderItem
    from app.models.user import User


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False, default=0)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="products",
    )
    created_by: Mapped["User"] = relationship(
        "User",
        back_populates="products",
    )
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="product",
        cascade="all, delete-orphan",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product",
    )