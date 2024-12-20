from fastapi import APIRouter
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.products import router as product_router
from app.api.v1.endpoints.orders import router as order_router
from app.api.v1.endpoints.categories import router as category_router

from app.api.v1.admin.products import router as admin_product_router
from app.api.v1.admin.auth import router as admin_auth_router
from app.api.v1.admin.brands import router as admin_brand_router
from app.api.v1.admin.categories import router as admin_category_router
from app.api.v1.admin.users import router as admin_user_router
from app.api.v1.admin.images import router as auth_image_router
from app.api.v1.admin.product_images import router as admin_image_router
from app.api.v1.admin.product_attributes import router as admin_product_attribute_router
from app.api.v1.admin.orders import router as admin_order_router

api_router = APIRouter()

# Add customer auth router
api_router.include_router(auth_router, prefix="/auth", tags=["customer-login"])

# Add product router
api_router.include_router(product_router, prefix="/products", tags=["products"])

# Add order router
api_router.include_router(order_router, prefix="/orders", tags=["orders"])

# Add category router
api_router.include_router(category_router, prefix="/categories", tags=["categories"])


# Add admin auth router
api_router.include_router(admin_auth_router, prefix="/admin/auth", tags=["admin-login"])

# Add admin product router
api_router.include_router(
    admin_product_router, prefix="/admin/products", tags=["product-management"]
)

# Add admin brand router
api_router.include_router(
    admin_brand_router, prefix="/admin/brands", tags=["brand-management"]
)

# Add admin category router
api_router.include_router(
    admin_category_router, prefix="/admin/categories", tags=["category-management"]
)

# Add admin user router
api_router.include_router(
    admin_user_router, prefix="/admin/users", tags=["user-management"]
)

# Add admin image router
api_router.include_router(
    auth_image_router, prefix="/admin/images", tags=["image-management"]
)

# Add admin product image router
api_router.include_router(
    admin_image_router,
    prefix="/admin/product-images",
    tags=["product-image-management"],
)

# Add admin product attribute router
api_router.include_router(
    admin_product_attribute_router,
    prefix="/admin/product-attributes",
    tags=["product-attribute-management"],
)

# Add admin order router
api_router.include_router(
    admin_order_router, prefix="/admin/orders", tags=["order-management"]
)
