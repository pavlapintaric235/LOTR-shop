from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.order import Order
    from app.models.product import Product


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="created_by",
    )
    carts: Mapped[list["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
    )