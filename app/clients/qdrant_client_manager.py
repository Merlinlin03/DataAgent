import asyncio
from random import random
from typing import Optional
from qdrant_client import AsyncQdrantClient, models
from app.conf.app_config import QdrantConfig, app_config

class QdrantClientManager:
    """
    进行向量存储和搜索的qdrant的客户端器类
    """
    def __init__(self, config: QdrantConfig):
        self.config = config
        self.client: Optional[AsyncQdrantClient] = None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncQdrantClient(
            url=self._get_url(),
            grpc_port=6334,
            prefer_grpc=True,
            check_compatibility=False,
        )

    async def close(self):
        await self.client.close()

# 创建客户端管理器
qdrant_client_manager = QdrantClientManager(app_config.qdrant)

if __name__ == "__main__":
    async def test():
        qdrant_client_manager.init()

        client = qdrant_client_manager.client

        collection_name = "my_collection"

        # 创建集合， 如果不存在才创建
        # if await not client.collection_exists(collection_name=collection_name):
        #     await client.create_collection(
        #         collection_name=collection_name, # 集合名称
        #         vectors_config=models.VectorParams(
        #             size=10,  # 向量的维度
        #             distance=models.Distance.COSINE  # 余弦相似匹配
        #         ),
        #     )
        # 创建集合 如果存在删除再创建
        if await client.collection_exists(collection_name=collection_name):
            await client.delete_collection(collection_name=collection_name)
        await client.create_collection(
            collection_name=collection_name, # 集合名称
            vectors_config=models.VectorParams(
                size=10,  # 向量的维度
                distance=models.Distance.COSINE  # 余弦相似匹配
            ),
        )

        # 插入数据
        await client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=i,
                    payload={ # 负载数据
                        # "color": f"red{i}",
                        "color": "red" if i % 2 == 0 else "blue",
                    },
                    vector=[random() for _ in range(10)], # 生成一个10维的向量数据
                )
                for i in range(100)
            ],
        )

        # 查询数据
        result = await client.query_points(
            collection_name=collection_name,
            query=[random() for _ in range(10)],
            limit=10, # 限制只取前2条
            score_threshold = 0.8, # 匹配相似度的临界值，小于这个值的所有点忽略
            query_filter=models.Filter( #  过滤条件： 根据携带的数据来进行过滤
                must=[models.FieldCondition(key="color", match=models.MatchValue(value="red"))]
            ),
        )

        print(result.points)
        print(len(result.points))

        await qdrant_client_manager.close()


    asyncio.run(test())
