from datetime import datetime

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DateInfoState, DBInfoState, DataAgentState
from app.core.log import logger


async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "补充日期和数据库环境"})
    try:
        dw_mysql_repo = runtime.context["dw_mysql_repo"]

        # 1.收集当前日期时间
        today = datetime.today()
        date = today.strftime("%Y-%m-%d")
        weekday = today.strftime("%A")
        quarter = f"Q{(today.month+2)//3}"  # Q1-Q4
        date_info = DateInfoState(
            date=date,
            weekday=weekday,
            quarter=quarter,
        )

        # 2.收集数据库信息
        db_info_mysql = await dw_mysql_repo.get_db_infos()
        db_info = DBInfoState(**db_info_mysql)

        logger.info(f"添加额外信息完成：date_info={date_info}, db_info={db_info}")

        return {"date_info": date_info, "db_info": db_info}
    except Exception as e:
        logger.error(f"添加额外信息信息失败：{str(e)}")
        raise
