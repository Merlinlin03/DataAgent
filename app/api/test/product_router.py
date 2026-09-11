from fastapi import APIRouter

# 管理product相关路由的路由器
product_router = APIRouter()

@product_router.get("/product/{id}")
def test(id: int):
    return {"id": id, "name": "prductt abc"}