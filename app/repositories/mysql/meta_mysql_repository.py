from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.column_metric_mysql import ColumnMetricMySQL
from app.models.mysql.metric_info_mysql import MetricInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL


class MetaMysqlRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    # 向table_info表中插入多条数据
    def save_table_infos(self, table_infos: list[TableInfoMySQL]):
        self.session.add_all(table_infos)

    # 向column_info表中插入多条数据
    def save_column_infos(self, column_infos: list[ColumnInfoMySQL]):
        self.session.add_all(column_infos)

    # 向metric_info表中插入多条数据
    def save_metric_infos(self, metric_infos: list[MetricInfoMySQL]):
        self.session.add_all(metric_infos)

    # 向column_metric表中插入多条数据
    def save_column_metrics(self, column_metrics: list[ColumnMetricMySQL]):
        self.session.add_all(column_metrics)

    # 根据字段id获取字段信息
    async def get_colun_info_by_id(self, column_id) ->ColumnInfoMySQL:
        return await self.session.get(ColumnInfoMySQL, column_id)

    # 根据表id获取表的主键和外键字段信息
    async def get_column_infos_by_table_id(self, table_id: str)->list[ColumnInfoMySQL]:
        result = await self.session.execute(
            Select(ColumnInfoMySQL)
                .where(ColumnInfoMySQL.table_id==table_id)
                .where(ColumnInfoMySQL.role.in_(["primary_key", "foreign_key"]))
        )

        return result.scalars().all()

    # 根据表id获取表信息
    async def get_table_info_by_table_id(self, table_id: str)->TableInfoMySQL:
        return await self.session.get(TableInfoMySQL, table_id)