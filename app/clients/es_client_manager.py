import asyncio
from typing import Optional
from elasticsearch import AsyncElasticsearch

from app.conf.app_config import ESConfig, app_config


class ESClientManager:
    def __init__(self, config: ESConfig):
        self.config = config
        self.client: Optional[AsyncElasticsearch] = None

    def init(self):
        self.client = AsyncElasticsearch(self._get_url())

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    async def close(self):
        await self.client.close()

es_client_manager = ESClientManager(app_config.es)

if __name__ == "__main__":
    async def test():
        es_client_manager.init()
        client = es_client_manager.client
        index_name = "test_index"

        # 创建index
        if await client.indices.exists(index=index_name):
            await client.indices.delete(index=index_name)
        await client.indices.create(
            index=index_name,
            mappings={
                "dynamic": False,
                "properties": {
                    "name": {
                        "type": "text"
                    },
                    "author": {
                        "type": "text"
                    },
                    "release_date": {
                        "type": "date",
                        "format": "yyyy-MM-dd"
                    },
                    "page_count": {
                        "type": "integer"
                    }
                }
            },
        )

        # 批量插入多个文档
        await client.bulk(
            operations=[
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Revelation Space",
                    "author": "Alastair Reynolds",
                    "release_date": "2000-03-15",
                    "page_count": 585
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "1984",
                    "author": "George Orwell",
                    "release_date": "1985-06-01",
                    "page_count": 328
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Fahrenheit 451",
                    "author": "Ray Bradbury",
                    "release_date": "1953-10-15",
                    "page_count": 227
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "Brave New World",
                    "author": "Aldous Huxley",
                    "release_date": "1932-06-01",
                    "page_count": 268
                },
                {
                    "index": {
                        "_index": index_name
                    }
                },
                {
                    "name": "The Handmaids Tale",
                    "author": "Margaret Atwood",
                    "release_date": "1985-06-01",
                    "page_count": 311
                }
            ],
            # refresh=True, # 自动刷新  每插入一个文档就刷新一下  性能低
        )

        # 等待1S后再查询
        # await asyncio.sleep(1)
        # 在搜索前手动刷新一下
        await client.indices.refresh(index=index_name)

        # 搜索
        result = await client.search(
            index=index_name,
            query={
                "match": {
                    "name": "brave"
                }
            },
        )
        print(result)
        print(result["hits"]["hits"][0]["_source"])

        await es_client_manager.close()


    asyncio.run(test())