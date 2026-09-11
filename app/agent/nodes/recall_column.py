from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.llm import llm
from app.agent.state import DataAgentState
from app.core.log import logger
from app.models.qdrant.column_info_qdrant import ColumnInfoQdrant
from app.prompt.prompt_loader import load_prompt

"""
0. 对query进行大模型语义化的分词，并与jiaba分词合并
1. 拿各个分词去做召回
2. 去查询qdrant向量库
3. 得到字段信息列表： list[ColumnInfoQdrant]
4. 返回字段信息列表： list[ColumnInfoQdrant]
"""
async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    runtime.stream_writer({"stage": "召回运营字段"})

    try:
        query = state["query"]
        keywords = state["keywords"]
        embedding_client = runtime.context["embedding_client"]
        column_qdrant_repository = runtime.context["column_qdrant_repo"]

        # 0.对query进行大模型语义化的分词，并与jiaba分词合并

        prompt_template = PromptTemplate(
            template=load_prompt("extend_keywords_for_column_recall"),
            input_variables=["query"],
        )
        output_parser = JsonOutputParser()
        chain = prompt_template | llm | output_parser
        result = await chain.ainvoke({"query": query})
        logger.info(f"recall_column llm keywords: {result}")
        keywords = list(set(keywords + result))

        # 用来保存所有召回的字段信息对象，需要去重：key: column_id
        column_infos_dict: dict[str, ColumnInfoQdrant] = {}
        # 1.# 拿各个分词去做召回
        for keyword in keywords:
            # 将keyword转换为向量
            vector = await embedding_client.aembed_query(keyword)
            # 2.去查询qdrant向量库, 得到字段信息列表： list[ColumnInfoQdrant]
            column_infos: list[ColumnInfoQdrant] = await column_qdrant_repository.search(vector)
            # 对查询得到的列表数据进行去重保存
            for column_info in column_infos:
                column_id = column_info["id"]
                if column_id not in column_infos_dict:
                    column_infos_dict[column_id] = column_info
        # 生成目标数据结构
        recall_columns: list[ColumnInfoQdrant] = list(column_infos_dict.values())

        logger.info(f"召回字段完成：{recall_columns}")
        # 3.# 返回字段信息列表： list[ColumnInfoQdrant]
        return {"recall_columns": recall_columns}
    except Exception as e:
        logger.error(f"召回字段失败：{str(e)}")
        raise
