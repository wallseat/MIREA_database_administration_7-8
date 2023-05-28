from fastapi import APIRouter

from .auth import router as role_auth
from .category import router as category_router
from .product import router as product_router
from .role import router as role_router
from .user import router as user_router

router = APIRouter()

router.include_router(user_router, prefix="/user")
router.include_router(category_router, prefix="/category")
router.include_router(product_router, prefix="/product")
router.include_router(role_router, prefix="/role")
router.include_router(role_auth, prefix="/auth")

__all__ = ["router"]
