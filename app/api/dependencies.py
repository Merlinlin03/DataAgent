from fastapi import Depends
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.query_service import QueryService


async def get_dw_session():
    """
        请求进来 → 进入 async with（创建 session）→ yield 暂停，把 session 交给路由函数
                                                          ↓
                                              路由函数使用 session 执行业务逻辑
                                                          ↓
        路由函数返回 → 回到 yield 后面的位置 → 退出 async with（自动关闭/归还 session）→ 请求结束
    """
    async with dw_mysql_client_manager.session_factory() as session:
        yield session # 返回session给调用，当前暂停，当 调用者执行完成回到当前yield后面执行，退出async with, 关闭session
        # return session  # 立即返回，退出async with 自动关闭session =》路由中调用的业务对象不再使用使用session了

def get_dw_mysql_repo(session: AsyncSession=Depends(get_dw_session)):
    return DWMysqlRepository(session)


async def get_meta_session():
    async with meta_mysql_client_manager.session_factory() as session:
        yield session


def get_meta_mysql_repo(session: AsyncSession = Depends(get_meta_session)):
    return MetaMysqlRepository(session)

def get_value_es_repo():
    return ValueESRepository(es_client_manager.client)

def get_column_qdrant_repo():
    return ColumnQdrantRepository(qdrant_client_manager.client)

def get_metric_qdrant_repo():
    return MetricQdrantRepository(qdrant_client_manager.client)

def get_embedding_client():
    return embedding_client_manager.client

def get_query_service(
    dw_mysql_repo: DWMysqlRepository = Depends(get_dw_mysql_repo),
    meta_mysql_repo: MetaMysqlRepository = Depends(get_meta_mysql_repo),
    value_es_repo: ValueESRepository =  Depends(get_value_es_repo),
    column_qdrant_repo: ColumnQdrantRepository =  Depends(get_column_qdrant_repo),
    metric_qdrant_repo: MetricQdrantRepository =  Depends(get_metric_qdrant_repo),
    embedding_client: HuggingFaceEndpointEmbeddings = Depends(get_embedding_client)
):
    return QueryService(
        dw_mysql_repo=dw_mysql_repo,
        meta_mysql_repo=meta_mysql_repo,
        value_es_repo=value_es_repo,
        column_qdrant_repo=column_qdrant_repo,
        metric_qdrant_repo=metric_qdrant_repo,
        embedding_client=embedding_client
    )