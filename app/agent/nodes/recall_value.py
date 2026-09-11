from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.models.es.value_info_es import ValueInfoES
from app.prompt.prompt_loader import load_prompt

"""
0. 对query进行大模型语义化的分词，并与jiaba分词合并
1. 拿各个分词去做召回
2. 去查询ES全文索引库
3. 得到字段信息列表： list[ValueInfoES]
4. 返回字段信息列表： list[ValueInfoES]
"""
async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "匹配国家渠道版本"})

    try:
        query = state["query"]
        keywords = state["keywords"]
        value_es_repo = runtime.context["value_es_repo"]

        # 0.对query进行大模型语义化的分词，并与jiaba分词合并
        prompt_template = PromptTemplate(
            template=load_prompt("extend_keywords_for_value_recall"),
            input_variables=["query"],
        )
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser
        result = await chain.ainvoke({"query": query})
        logger.info(f"recall_value llm keywords: {result}")
        keywords = list(set(keywords + result))

        # 用来保存所有召回的字段信息对象，需要去重：key: value_id
        value_infos_dict: dict[str, ValueInfoES] = {}
        # 1.# 拿各个分词去做召回
        for keyword in keywords:
            # 2.去查询ES库, 得到字段值信息列表： list[ValueInfoES]
            value_infos: list[ValueInfoES] = await value_es_repo.search(keyword)
            # 对查询得到的列表数据进行去重保存
            for value_info in value_infos:
                value_id = value_info["id"]
                if value_id not in value_infos_dict:
                    value_infos_dict[value_id] = value_info
        # 3. 生成目标数据结构
        recall_values: list[ValueInfoES] = list(value_infos_dict.values())

        logger.info(f"召回字段值完成：{recall_values}")
        # 4. 返回字段取值列表： list[valueInfoQdrant]
        return {"recall_values": recall_values}
    except Exception as e:
        logger.error(f"召回字段值失败：{e}")
        raise
