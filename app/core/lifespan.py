from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # print("应用初始时执行一次, 做一次的初始化工作")
    # 初始化客户端管理器
    embedding_client_manager.init()
    es_client_manager.init()
    dw_mysql_client_manager.init()
    meta_mysql_client_manager.init()
    qdrant_client_manager.init()

    yield

    # print("应用停止前执行一次， 做一次的收尾工作")
    # 关闭客户端管理器
    await es_client_manager.close()
    await dw_mysql_client_manager.close()
    await meta_mysql_client_manager.close()
    await qdrant_client_manager.close()