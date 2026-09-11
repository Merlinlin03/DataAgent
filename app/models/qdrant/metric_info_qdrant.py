from typing import TypedDict

# 定义qdrant中保存的指标信息的模型
class MetricInfoQdrant(TypedDict):
    id:str
    name:str
    description:str
    relevant_columns:list
    alias:list