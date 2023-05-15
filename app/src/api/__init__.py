from fastapi import APIRouter

from .category import router as category_router
from .product import router as product_router
from .user import router as user_router

router = APIRouter()

router.include_router(user_router, prefix="/user")
router.include_router(category_router, prefix="/category")
router.include_router(product_router, prefix="/product")

__all__ = ["router"]
