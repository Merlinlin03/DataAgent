import yaml
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.prompt.prompt_loader import load_prompt


async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "筛选必要指标"})
    try:
        query = state["query"]
        metric_infos = state["metric_infos"]

        # 1. 调用模型，过滤掉不需要指标，生成需要的指标名的列表
        prompt_template = PromptTemplate(
            template=load_prompt("filter_metric_info"),
            input_variables=["query", "metric_infos"],
        )
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser
        result = await chain.ainvoke({"query": query, "metric_infos": yaml.dump(
                metric_infos,
                allow_unicode=True, # 保留中文原文，不转换为unicode编码  ‘\u5317\u4eac’
                sort_keys=False, # 不要对数据中的字典中的属性进行排序，保持原来的顺序
            )})
        # [指标1， 指标2]

        # 2. 去对metric_infos中的指标进行过滤
        for metric_info in metric_infos[:]:
            table_name = metric_info["name"]
            if table_name not in result:
                metric_infos.remove(metric_info)

        logger.info(f"过滤指标完成：{metric_infos}")

        return {"metric_infos": metric_infos}
    except Exception as e:
        logger.error(f"过滤指标信息失败：{str(e)}")
        raise
