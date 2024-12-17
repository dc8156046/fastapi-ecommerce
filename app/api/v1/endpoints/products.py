from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Get products list")
def get_products():
    return {"message": "普通用户可以查看的产品列表"}


@router.get("/{product_id}", summary="Get product detail")
def get_product(product_id: int):
    return {"message": f"普通用户可以查看的产品详情，产品ID: {product_id}"}
