import uuid

import uvicorn
from fastapi import FastAPI, Request

from app.api.routers.query_router import query_router
from app.core.context import set_req_id
from app.core.lifespan import lifespan

# 创建应用对象
app = FastAPI(
    title="海外运营智数平台",
    description="面向海外产品运营的自然语言问数与指标分析服务",
    version="1.0.0",
    lifespan=lifespan,
)


# 注册查询的路由器
app.include_router(query_router)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # 处理请求前执行
    # print("处理请求前执行....")
    # 给每个请求保存一个唯一的请求id
    set_req_id(str(uuid.uuid4()))

    # 调用下一个中间件或目标路由，返回值是目标路由返回的响应
    return await call_next(request)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
