from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.core.log import logger


async def validate_sql(state, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "校验 SQL 安全性"})

    sql = ''
    try:
        sql = state["sql"]
        dw_mysql_repo = runtime.context["dw_mysql_repo"]

        # 检查SQL语法是否合法
        await dw_mysql_repo.validate_sql(sql)

        logger.info(f"校验SQL成功：{sql}")
        return {"error": None}
    except Exception as e:
        logger.error(f"校验SQL失败：{sql}")
        return {"error": f"SQL语法错误：{str(e)}"}
        # raise
