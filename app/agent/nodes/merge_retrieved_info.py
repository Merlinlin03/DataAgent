from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, MetricInfoState, ColumnInfoState, TableInfoState
from app.core.log import logger
from app.models.es.value_info_es import ValueInfoES
from app.models.mysql.column_info_mysql import ColumnInfoMySQL
from app.models.mysql.table_info_mysql import TableInfoMySQL
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.models.qdrant.metric_info_qdrant import MetricInfoQdrant


async def merge_retrieved_info(state:DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "合并数仓上下文"})
    try:
        # 取出相关的数据
        recall_columns: list[ColumnInfoQdrant] = state["recall_columns"]
        recall_metrics: list[MetricInfoQdrant] = state["recall_metrics"]
        recall_values: list[ValueInfoES] = state["recall_values"]
        meta_mysql_repo = runtime.context["meta_mysql_repo"]

        # 1. 收集最完整的字段信息列表

        # 1.1 根据recall_columns来创建
        column_infos_dict: dict[str, ColumnInfoQdrant] = {item["id"]: item for item in recall_columns}
        # 1.2 补充1：recall_metrics对应的字段
        for metric in recall_metrics:
            for relevant_column_id in metric["relevant_columns"]:
                if relevant_column_id not in column_infos_dict:
                    column_info_mysql: ColumnInfoMySQL = await meta_mysql_repo.get_colun_info_by_id(relevant_column_id)
                    column_infos_dict[relevant_column_id] = _convert_column_info_mysql_to_qdrant(column_info_mysql)
        # 1.3. 补充2： 字段值对应的字段  内部还需要将当前字段值添加到字段的examples中
        for recall_value in recall_values:
            column_id = recall_value["column_id"]
            if column_id not in column_infos_dict:
                column_info_mysql: ColumnInfoMySQL = await meta_mysql_repo.get_colun_info_by_id(column_id)
                column_infos_dict[column_id] = _convert_column_info_mysql_to_qdrant(column_info_mysql)
            if recall_value["value"] not in column_infos_dict[column_id]["examples"]:
                column_infos_dict[column_id]["examples"].append(recall_value["value"])

        # 对字段信息列表按表分组存储： dict[table_id, list[ColumnInfoQdrant]]
        table_column_infos_dict: dict[str, list[ColumnInfoQdrant]] = {}
        # column_infos_dict: dict[str, ColumnInfoQdrant]
        for column_info in column_infos_dict.values():
            if column_info["table_id"] not in table_column_infos_dict:
                table_column_infos_dict[column_info["table_id"]] = []
            table_column_infos_dict[column_info["table_id"]].append(column_info)

        table_infos: list[TableInfoState] = []

        # 补充3：将相关表的主键和外键字段添加到列表中
        for table_id, column_infos in table_column_infos_dict.items():
            # 去meta库取当前表的主键和外键字段
            pf_column_infos: list[ColumnInfoMySQL] = await meta_mysql_repo.get_column_infos_by_table_id(table_id)
            for pf_column_info in pf_column_infos:
                if pf_column_info.id not in column_infos_dict:
                    table_column_infos_dict[table_id].append(_convert_column_info_mysql_to_qdrant(pf_column_info))

            # 2. 生成TableInfoState的对象列表
            # 2.1 查询当前表信息
            table_info_mysql: TableInfoMySQL = await meta_mysql_repo.get_table_info_by_table_id(table_id)
            # 2.2 得到当前表的所字段状态信息对象列表
            columns: list[ColumnInfoState] = [_convert_column_info_qdrant_to_state(item) for item in column_infos]
            # 2.3 创建TableInfoState对象, 添加到列表
            table_infos.append(TableInfoState(
                name=table_info_mysql.name,
                role=table_info_mysql.role,
                description=table_info_mysql.description,
                columns=columns
            ))

        # 处理指标列表
        metric_infos = [
            _convert_metric_info_qdrant_to_state(item)
            for item in recall_metrics
        ]

        logger.info(f"合并表信息列表完成： {table_infos}")
        logger.info(f"合并处理指标列表完成：{metric_infos}")

        return {"table_infos": table_infos, "metric_infos": metric_infos}
    except Exception as e:
        logger.error(f"合并召回失败：{str(e)}")

def _convert_column_info_qdrant_to_state(column:ColumnInfoQdrant)->ColumnInfoState:
    return ColumnInfoState(
        name=column['name'],
        type=column['type'],
        role=column["role"],
        examples=column["examples"],
        description=column["description"],
        alias=column["alias"]
    )


def _convert_metric_info_qdrant_to_state(recall_metric:MetricInfoQdrant):
    return MetricInfoState(
        name=recall_metric['name'],
        description=recall_metric["description"],
        relevant_columns=recall_metric["relevant_columns"],
        alias=recall_metric["alias"]
    )

def _convert_column_info_mysql_to_qdrant(column_info_mysql:ColumnInfoMySQL)->ColumnInfoQdrant:
    return ColumnInfoQdrant(
        id=column_info_mysql.id,
        name=column_info_mysql.name,
        description=column_info_mysql.description,
        role=column_info_mysql.role,
        type=column_info_mysql.type,
        examples=column_info_mysql.examples,
        table_id=column_info_mysql.table_id,
        alias=column_info_mysql.alias
    )
