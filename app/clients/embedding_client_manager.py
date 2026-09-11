import asyncio
from typing import Optional
from app.conf.app_config import EmbeddingConfig, app_config
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings


class EmbeddingClientManager:
    """
    生成向量数据的客户端器类
    """
    def __init__(self, config: EmbeddingConfig):
        self.config = config
        self.client: Optional[HuggingFaceEndpointEmbeddings] = None

    def _get_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(model=self._get_url())

# 创建客户端管理器
embedding_client_manager = EmbeddingClientManager(app_config.embedding)

if __name__ == "__main__":
    async def test():
        embedding_client_manager.init()

        # 对指定文本进行向量化
        text = "hello world"
        result = embedding_client_manager.client.embed_query(text)
        print(result) # 包含1024个点数据的数组
        print(len(result))

    asyncio.run(test())
