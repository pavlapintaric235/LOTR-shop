from decimal import Decimal

from sqlalchemy import delete, select # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore

from app.core.security import get_password_hash
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.user import User


PRODUCTS = [
    {
        "category_slug": "clothes",
        "slug": "elven-cloak",
        "name": "Elven Cloak",
        "description": "A travel cloak inspired by Lothlorien.",
        "price": Decimal("79.99"),
        "stock": 12,
        "image_url": "/static/images/products/elven-cloak.jpg",
        "is_featured": True,
    },
    {
        "category_slug": "clothes",
        "slug": "gondor-ranger-cloak",
        "name": "Gondor Ranger Cloak",
        "description": "A ranger-style cloak inspired by the men of Gondor.",
        "price": Decimal("89.99"),
        "stock": 8,
        "image_url": "/static/images/products/gondor-ranger-cloak.jpg",
        "is_featured": False,
    },
    {
        "category_slug": "clothes",
        "slug": "fellowship-travel-tunic",
        "name": "Fellowship Travel Tunic",
        "description": "A travel tunic inspired by the Fellowship's journey.",
        "price": Decimal("64.99"),
        "stock": 10,
        "image_url": "/static/images/products/fellowship-travel-vest.jpg",
        "is_featured": False,
    },
    {
        "category_slug": "movie-props",
        "slug": "anduril-replica",
        "name": "Anduril Replica",
        "description": "Decorative sword replica inspired by Aragorn's blade.",
        "price": Decimal("249.99"),
        "stock": 3,
        "image_url": "/static/images/products/anduril-replica.jpg",
        "is_featured": True,
    },
    {
        "category_slug": "movie-props",
        "slug": "sting-replica",
        "name": "Sting Replica",
        "description": "Collector sword replica inspired by Frodo's blade.",
        "price": Decimal("149.00"),
        "stock": 5,
        "image_url": "/static/images/products/sting-replica.jpg",
        "is_featured": True,
    },
    {
        "category_slug": "movie-props",
        "slug": "one-ring-replica",
        "name": "One Ring Replica",
        "description": "A wearable replica inspired by the One Ring.",
        "price": Decimal("59.00"),
        "stock": 20,
        "image_url": "/static/images/products/the-one-ring-replica.jpg",
        "is_featured": True,
    },
    {
        "category_slug": "movie-props",
        "slug": "evenstar-pendant",
        "name": "Evenstar Pendant",
        "description": "A pendant inspired by Arwen's Evenstar.",
        "price": Decimal("159.00"),
        "stock": 4,
        "image_url": "/static/images/products/evenstar-pendant.jpg",
        "is_featured": False,
    },
    {
        "category_slug": "books",
        "slug": "red-book-of-westmarch",
        "name": "Red Book of Westmarch",
        "description": (
            "A collector-style journal inspired by "
            "Bilbo and Frodo's record."
        ),
        "price": Decimal("39.99"),
        "stock": 7,
        "image_url": "/static/images/products/red-book-of-westmarch.jpg",
        "is_featured": False,
    },
    {
        "category_slug": "books",
        "slug": "the-silmarillion-collector-edition",
        "name": "The Silmarillion Collector Edition",
        "description": "Collector's edition of The Silmarillion.",
        "price": Decimal("28.00"),
        "stock": 6,
        "image_url": "/static/images/products/the-silmarillion-collector-edition.jpg",
        "is_featured": True,
    },
    {
        "category_slug": "books",
        "slug": "atlas-of-middle-earth",
        "name": "Atlas of Middle-earth",
        "description": "A reference atlas for Tolkien's world.",
        "price": Decimal("34.99"),
        "stock": 9,
        "image_url": "/static/images/products/atlas-of-middle-earth.jpg",
        "is_featured": False,
    },
]


async def reset_database_state(session: AsyncSession) -> None:
    await session.execute(delete(CartItem))
    await session.execute(delete(Cart))
    await session.execute(delete(OrderItem))
    await session.execute(delete(Order))
    await session.execute(delete(Product))
    await session.execute(delete(Category))
    await session.execute(delete(User))
    await session.commit()


async def _get_or_create_user(
    session: AsyncSession,
    *,
    username: str,
    email: str,
    password: str,
    is_admin: bool,
) -> User:
    result = await session.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            email=email,
            username=username,
            hashed_password=get_password_hash(password),
            is_admin=is_admin,
        )
        session.add(user)
        await session.flush()
        return user

    user.email = email
    user.hashed_password = get_password_hash(password)
    user.is_admin = is_admin
    await session.flush()
    return user


async def _get_or_create_category(
    session: AsyncSession,
    *,
    slug: str,
    name: str,
) -> Category:
    result = await session.execute(
        select(Category).where(Category.slug == slug)
    )
    category = result.scalar_one_or_none()

    if category is None:
        category = Category(slug=slug, name=name)
        session.add(category)
        await session.flush()
        return category

    category.name = name
    await session.flush()
    return category


async def _get_or_create_product(
    session: AsyncSession,
    *,
    item: dict,
    category_id: int,
    created_by_id: int,
) -> Product:
    result = await session.execute(
        select(Product).where(Product.slug == item["slug"])
    )
    product = result.scalar_one_or_none()

    if product is None:
        product = Product(
            slug=str(item["slug"]),
            name=str(item["name"]),
            description=str(item["description"]),
            price=item["price"],
            stock=int(item["stock"]),
            image_url=item["image_url"],
            is_featured=bool(item["is_featured"]),
            category_id=category_id,
            created_by_id=created_by_id,
        )
        session.add(product)
        await session.flush()
        return product

    product.name = str(item["name"])
    product.description = str(item["description"])
    product.price = item["price"]
    product.stock = int(item["stock"])
    product.image_url = item["image_url"]
    product.is_featured = bool(item["is_featured"])
    product.category_id = category_id
    product.created_by_id = created_by_id
    await session.flush()
    return product


async def seed_test_data(session: AsyncSession) -> None:
    admin = await _get_or_create_user(
        session,
        username="frodo",
        email="frodo@example.com",
        password="shire123",
        is_admin=True,
    )

    await _get_or_create_user(
        session,
        username="sam",
        email="sam@example.com",
        password="shire123",
        is_admin=False,
    )

    clothes = await _get_or_create_category(
        session,
        slug="clothes",
        name="Clothes",
    )
    movie_props = await _get_or_create_category(
        session,
        slug="movie-props",
        name="Movie Props",
    )
    books = await _get_or_create_category(
        session,
        slug="books",
        name="Books",
    )

    categories_by_slug = {
        "clothes": clothes,
        "movie-props": movie_props,
        "books": books,
    }

    for item in PRODUCTS:
        category = categories_by_slug[str(item["category_slug"])]
        await _get_or_create_product(
            session,
            item=item,
            category_id=category.id,
            created_by_id=admin.id,
        )

    await session.commit()