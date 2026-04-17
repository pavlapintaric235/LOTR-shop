from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint # type: ignore
from sqlalchemy.orm import Mapped, mapped_column, relationship # type: ignore

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.product import Product


class CartItem(Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_item_cart_product"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)

    cart: Mapped["Cart"] = relationship(
        "Cart",
        back_populates="items",
    )
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="cart_items",
    )