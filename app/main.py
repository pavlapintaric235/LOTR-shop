from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.cart import router as cart_router
from app.api.routes.categories import router as categories_router
from app.api.routes.frontend import router as frontend_router
from app.api.routes.health import router as health_router
from app.api.routes.orders import router as orders_router
from app.api.routes.payments import router as payments_router
from app.api.routes.products import router as products_router
from app.api.routes.testing import router as testing_router
from app.api.routes.users import router as users_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )

    app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(categories_router)
    app.include_router(products_router)
    app.include_router(admin_router)
    app.include_router(cart_router)
    app.include_router(orders_router)
    app.include_router(payments_router)

    if settings.testing_routes_enabled:
        app.include_router(testing_router)

    app.include_router(frontend_router)

    return app


app = create_app()