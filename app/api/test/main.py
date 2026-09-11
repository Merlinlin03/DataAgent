"""
测试1: 测试不同类型的请求
测试2：获取不同类型的参数
测试3：使用路由器
测试4：流式输出
测试5：生命周期
测试6：中间件
测试7：依赖注入   DI  Depend Inject
"""
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request, Depends
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from app.api.test.order_router import order_router
from app.api.test.product_router import product_router
from app.clients.es_client_manager import es_client_manager
from app.repositories.es.value_es_repository import ValueESRepository

"""
测试5：生命周期
"""
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("应用初始时执行一次, 做一次的初始化工作")
    yield
    print("应用停止前执行一次， 做一次的收尾工作")

# 创建FastAPI的应用对象
app = FastAPI(lifespan=lifespan)

"""
测试6：中间件
"""
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    # 处理请求前执行
    print("处理请求前执行....")
    # 调用下一个中间件或目标路由，返回值是目标路由返回的响应
    response = await call_next(request)
    # 处理请求后执行
    print("处理请求后执行....")
    return response


"""
测试7：依赖注入(DI  Depend Inject)
"""
def get_value_es_repo():
    print("get_value_es_repo()")
    es_client_manager.init()
    return ValueESRepository(es_client_manager.client)


@app.get("/di/{id}")
def test_di(id: int, value_es_repo: ValueESRepository=Depends(get_value_es_repo)):
    print(f"处理 /di/{id} 的请求 value_es_repo={value_es_repo}")
    return {"id": id, "name": "abc"}



"""测试1: 测试不同类型的请求"""
# 注册路由接口
# 当这个路由路径被请求时，会自动调用路由函数
@app.get("/xxx")
async def test_get():
    print("处理 /xxx get的请求。。。")
    return {"get message": "Hello World2222333"}  # response：服务器端给浏览器端的响应数据
@app.post("/xxx")
async def test_post():
    print("处理 /xxx post 的请求。。。")
    return {"post message": "Hello World2222333"}

"""
测试2：获取不同类型的参数
1. query参数: 请求路径中？后面的参数
2. param参数：路径中可变的的部分
3. body参数：json格式
"""
class MyBody(BaseModel):
    age: int
    sex: str

@app.post("/api/user/{id}")
def test_three_params(body: MyBody, id: int, name: str):
    print(f"处理多种参数的路由函数 body={body}, id={id}, name={name}")
    return {"id":id, "name":name, "age": body.age, "sex": body.sex}

"""
测试3：使用路由器
  操作order的有3个接口  order_router
  操作product的有4个接口  product_router
"""
# 注册路由器
app.include_router(product_router, prefix="/v1")
app.include_router(order_router, prefix="/v2")

"""
测试4：SSE流式响应
"""
async def fake_video_streamer():
    for i in range(10):
        yield 'data: {"name": "Tom", "age": 18} \n\n'
        await asyncio.sleep(1)

async def call_async():
    async for chunk in fake_video_streamer():
        print(chunk)

@app.get("/api/stream")
async def test_stream():
    return StreamingResponse(fake_video_streamer(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
    # asyncio.run(call_async())