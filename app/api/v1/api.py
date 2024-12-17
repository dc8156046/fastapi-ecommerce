from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.products import router as product_router
from app.api.v1.admin.products import router as admin_product_router
from app.api.v1.admin.auth import router as admin_auth_router
from app.api.v1.admin.brands import router as admin_brand_router


api_router = APIRouter()

# Add admin auth router
api_router.include_router(admin_auth_router, prefix="/admin/auth", tags=["admin"])

# Add customer auth router
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])

# Add product router
api_router.include_router(product_router, prefix="/products", tags=["products"])

# Add admin router
api_router.include_router(
    admin_product_router, prefix="/admin/products", tags=["admin"]
)

# Add admin brand router
api_router.include_router(admin_brand_router, prefix="/admin/brands", tags=["admin"])
