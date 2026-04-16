import asyncio

from app.db.base_class import Base
from app.db.session import SessionLocal, engine
from app.models.cart import Cart  # noqa: F401
from app.models.cart_item import CartItem  # noqa: F401
from app.models.category import Category  # noqa: F401
from app.models.order import Order  # noqa: F401
from app.models.order_item import OrderItem  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.user import User  # noqa: F401
from app.services.seed import seed_test_data


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        await seed_test_data(session)

    print("Database tables created and demo data seeded.")


if __name__ == "__main__":
    asyncio.run(main())