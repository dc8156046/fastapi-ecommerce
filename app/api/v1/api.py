from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.products import router as product_router
from app.api.v1.admin.admin_products import router as admin_product_router
from app.api.v1.admin.auth import router as admin_auth_router

api_router = APIRouter()
api_router.include_router(
    admin_auth_router, prefix="/admin/auth", tags=["admin"]
)  # Add admin auth router
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])  # Add auth router
api_router.include_router(
    product_router, prefix="/products", tags=["products"]
)  # Add product router
api_router.include_router(
    admin_product_router, prefix="/admin/products", tags=["admin"]
)  # Add admin router
