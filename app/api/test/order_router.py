from fastapi import APIRouter

# 管理order相关路由的路由器
order_router = APIRouter()

@order_router.get("/order/{id}")
def test(id: int):
    return {"id": id, "name": "order cba"}