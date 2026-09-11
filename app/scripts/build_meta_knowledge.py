import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.embedding_client_manager import embedding_client_manager
from app.clients.es_client_manager import es_client_manager
from app.clients.mysql_client_manager import dw_mysql_client_manager, meta_mysql_client_manager
from app.clients.qdrant_client_manager import qdrant_client_manager
from app.conf.meta_config import meta_config
from app.core.log import logger
from app.models.mysql.base import Base
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.mysql.dw_mysql_repository import DWMysqlRepository
from app.repositories.mysql.meta_mysql_repository import MetaMysqlRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.services.meta_knowledge_service import MetaKnowledgeService

"""
1. 初始所有客户端管理器
2. 创建构建的业务对象,要准备
    创建依赖的所有持久层对象，传入依赖的session或client
    用来生成向量的客户端
3. 调用业务对象的构建方法来构建知识库
4. 如果成功了，提交事务
5。如果失败了，回滚事务
6. 最终都要关闭客户端管理器
"""
async def start_build():

    # 1. 初始所有客户端管理器
    embedding_client_manager.init()
    es_client_manager.init()
    dw_mysql_client_manager.init()
    meta_mysql_client_manager.init()
    qdrant_client_manager.init()

    try:
        async with meta_mysql_client_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        # 2. 创建构建的业务对象
        async with (dw_mysql_client_manager.session_factory() as dw_session,
                    meta_mysql_client_manager.session_factory() as meta_session):
            dw_session: AsyncSession
            meta_session: AsyncSession

            service = MetaKnowledgeService(
                dw_mysql_repo=DWMysqlRepository(dw_session),
                meta_myql_repo=MetaMysqlRepository(meta_session),
                value_es_repo=ValueESRepository(es_client_manager.client),
                column_qdrant_repo=ColumnQdrantRepository(qdrant_client_manager.client),
                metric_qdrant_repo=MetricQdrantRepository(qdrant_client_manager.client),
                embedding_client=embedding_client_manager.client
            )
            # 3. 调用构建方法
            await service.build(meta_config)
            # 4. 如果成功了，提交事务
            await dw_session.commit()
            await meta_session.commit()
            logger.info("构建成功了")

    except Exception as e:
        # 5。如果失败了，回滚事务
        await dw_session.rollback()
        await meta_session.rollback()
        logger.error(f"构建知识库失败： {str(e)}")
        raise   # 方便查看异常具体情况
    finally:
        # 6. 最终都要关闭客户端管理器
        await es_client_manager.close()
        await dw_mysql_client_manager.close()
        await meta_mysql_client_manager.close()
        await qdrant_client_manager.close()

if __name__ == "__main__":
    asyncio.run(start_build())
