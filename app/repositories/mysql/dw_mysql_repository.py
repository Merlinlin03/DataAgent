from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DWMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_column_types(self, table_name: str)->dict[str,str]:
        """获取当前表的所有字段的类型"""
        # 定义查询sql
        sql = f"show columns from {table_name}"
        # 执行sql
        result = await self.session.execute(text(sql))
        # 整理数据并返回
        return {row.Field:row.Type for row in result.all()}

    async def get_column_values(self, table_name:str, column_name:str, limit:int=10) ->list:
        """查询指定字段的前limit个字段值"""
        # 定义查询sql
        sql = f"select distinct {column_name} from {table_name} limit {limit}"
        # 执行sql
        result = await self.session.execute(text(sql))
        # 整理数据并返回
        return [_normalize_value(value) for value in result.scalars().all()]

    async def get_db_infos(self) ->dict[str,str]:
        result = await self.session.execute(text("select version()"))
        version = result.scalar()
        dialect = self.session.get_bind().dialect.name
        return {"version":version, "dialect":dialect}

    async def validate_sql(self, sql):
        """校验SQL"""
        # 它利用真实数据库的解析器，能发现表不存在、字段名拼写错误、JOIN 语法错误等实际问题
        # 不会执行SQL
        await self.session.execute(text(f"explain {sql}"))

    async def execute_sql(self, sql):
        """执行一条查询的SQL"""
        result = await self.session.execute(text(sql))
        # return result.mappings().all()   #rowMapping对象  不能直接序列化
        return [dict(row) for row in result.mappings().all()]  # 转换为了字典的数组 =》方便序列化为json字符串

    """
    序列化：将某种语言的对象或数组转为特定格式的字符串（json/yaml）
    反序列化：将特定格式的字符串转换为某种语言的对象或数组
    """


def _normalize_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value
