from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger


async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "查询运营数据仓库"})

    try:
        sql = state["sql"]
        dw_mysql_repo = runtime.context["dw_mysql_repo"]

        # 执行sql
        result = await dw_mysql_repo.execute_sql(sql)

        # 将查询结果写给调用者
        runtime.stream_writer({"result": result})

        logger.info(f"执行SQL完成 result={result}")
    except Exception as e:
        logger.error(f"执行SQL失败")
        raise
