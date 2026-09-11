from typing import TypedDict

# 定义es中保存的字段取值信息的模型
class ValueInfoES(TypedDict):
    id:str
    value:str
    type:str
    column_id:str
    column_name:str
    table_id:str
    table_name:str