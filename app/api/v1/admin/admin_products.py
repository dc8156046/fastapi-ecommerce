from fastapi import APIRouter

router = APIRouter()


@router.post("/admin/products", summary="创建产品")
def create_product():
    return {"message": "管理员创建了一个产品"}


@router.delete("/admin/products/{product_id}", summary="删除产品")
def delete_product(product_id: int):
    return {"message": f"管理员删除了产品，产品ID: {product_id}"}
