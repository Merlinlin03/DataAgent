
"""
ContextVar: 协程安全的上下文变量
    每个协程都有自己的上下文对象，互不干扰，可以向其中独立设置和获取不同变量名的数据
        =》协程1：context对象：{"aa": 数据1， "bb": 数据2}
        =》协程2：context对象：{"aa": 数据3， "bb": 数据4}
    我们可以通过ContextVar向当前协程的context对象中设置数据和获取数据
        context_var = ContextVar("aa", default="") => 协程1和协程2的context对象：{"aa": ""}
        => 协程1：context_var.set("1111")  => 协程1的context对象：{"aa": "1111"}
        => 协程2：context_var.set("2222")  => 协程2的context对象：{"aa": "2222"}
        => 协程1：context_var.get()  => "1111"
        => 协程2：context_var.get()  => "2222"
        => 协程1：context_var.reset() => 协程1的context对象: {}
    注意：ContextVar对象本身并不存储数据，数据存储在协程的context对象中 =》contextVar是context对象的代理对象
"""
import asyncio
from _contextvars import ContextVar, Token

_req_context_var = ContextVar("req_id", default="")

def set_req_id(request_id: str)->Token:
    return _req_context_var.set(request_id)  # 向当前协和的context对象中保存数据

def get_req_id()->str:
    return _req_context_var.get()

def reset_req_id(token: Token):
    _req_context_var.reset(token)

if __name__ == '__main__':
    async def req1():
        print(f"before req1 req_id= {get_req_id()}")
        token = set_req_id("1111")
        await asyncio.sleep(1) # 模拟处理一定的时间
        print(f"after req1 req_id= {get_req_id()}")
        reset_req_id(token)
        print(f"after reset req1 req_id= {get_req_id()}")

    async def req2():
        print(f"before req2 req_id= {get_req_id()}")
        token = set_req_id("2222")
        await asyncio.sleep(1)  # 模拟处理一定的时间
        print(f"after req2 req_id= {get_req_id()}")
        reset_req_id(token)
        print(f"after reset req2 req_id= {get_req_id()}")

    async def test():
        await asyncio.gather(req1(), req2())

    asyncio.run(test())