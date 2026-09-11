"""
状态图：StateGraph的实例
节点： 实现特定功能的函数
状态: 包含多个可变数据的对象，在图的各个节点上流转
边: 它是AB 2个节点连线， A执行后执行B,且将最新的状态数据传递给B

节点函数中的参数：
    state: 状态对象
    runtime: Runtime   运行时对象，包含下面
        stream_writer: 向调用者输出自定义数据的函数
        store: 实现跨会话长期记忆的对象，默认是存在内存中
        context: 包含指定固定数据或依赖外部模块对象
    config: 保存配置的对象，比如执行时指定的thread_id
stream_mode:
    updates: 外部得到的是节点返回的更新
    values: 节点返回后合并后的state值
    custom: 外部得到的是自定义的数据
"""
import asyncio
from typing import TypedDict

from langchain_core.runnables import configurable, RunnableConfig
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

# 定义状态类型
class MyState(TypedDict):
    query: str
    keywords:list[str]
    sql: str
# 自定义Context类型
class MyContext(TypedDict):
    db_name: str
    # 可以有其它的功能模块对象  ，比如: dw_mysql_repository

def extrict_keywords(state:MyState, runtime: Runtime[MyContext], config: RunnableConfig):
    print(f"执行 extrict_keywords节点 ")
    print(state)
    print(f"开始对{state["query"]}进行分词")

    runtime.stream_writer("提取关键字")
    # 测试context
    context = runtime.context
    print(f"context db={context["db_name"]}")
    # 测试config
    print(f"config={config}")

    keywords: list[str] = ["你", "是", "谁"]

    # 不要直接修改state,它应该是读
    # state["keywords"] = keywords
    # 返回要产生的新数据
    return {"keywords": keywords}  # graph会自动合并  reducer

def genarate_sql(state, runtime: Runtime):
    print(f"执行 genarate_sql节点 ")
    print(state)
    print("开始生成SQL")

    runtime.stream_writer("生成SQL")


    sql = "select * from customer"
    return {"sql": sql}

graph_builder = StateGraph(state_schema=MyState, context_schema=MyContext)
# 添加节点
graph_builder.add_node("extrict_keywords", extrict_keywords)
graph_builder.add_node("genarate_sql", genarate_sql)

# 添加边
graph_builder.add_edge(START, "extrict_keywords")
graph_builder.add_edge("extrict_keywords", "genarate_sql")
graph_builder.add_edge("genarate_sql", END)


# 编译
graph = graph_builder.compile()

# 运行
if __name__ == "__main__":
    async def test():
        state = MyState(query="你是谁")
        context = MyContext(db_name="aaa")
        """
        stream_mode:
            updates: 外部得到的是节点返回的更新
            values: 节点返回后合并后的state值
            custom: 外部得到的是自定义的数据
        """
        async for chunk in graph.astream(
                input=state,
                context=context,
                stream_mode="custom",
                config={"thread_id": 1}
        ):
            print('---', chunk)


    asyncio.run(test())