from typing import TypedDict

# 定义qdrant中保存的字段信息的模型
class ColumnInfoQdrant(TypedDict):
    id: str
    name: str
    type:str
    role: str
    examples:list
    description:str
    alias: list
    table_id: str