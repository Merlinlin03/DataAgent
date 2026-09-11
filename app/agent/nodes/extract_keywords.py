from jieba.analyse import extract_tags
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

"""
利用Jiaba对提问进行一个基本非语义分词，可能会丢失语义的词，需要后面的节点对提问进行语义分词补充
"""
def extract_keywords(state: DataAgentState, runtime: Runtime[DataAgentContext])->dict:
    runtime.stream_writer({"stage": "理解运营问题"})

    try:
        # 得到提问
        query = state["query"]

        # 使用jiaba进行分词
        # 定义返回指定词性的元组
        allow_pos = (
            "n",  # 名词: 数据、服务器、表格
            "nr",  # 人名: 张三、李四
            "ns",  # 地名: 北京、上海
            "nt",  # 机构团体名: 政府、学校、某公司
            "nz",  # 其他专有名词: Unicode、哈希算法、诺贝尔奖
            "v",  # 动词: 运行、开发
            "vn",  # 名动词: 工作、研究
            "a",  # 形容词: 美丽、快速
            "an",  # 名形词: 难度、合法性、复杂度
            "eng",  # 英文
            "i",  # 成语
            "l",  # 常用固定短语
        )
        result = extract_tags(query, topK=10, allowPOS=allow_pos)
        logger.info(f"提取的关键字为：{result}")
        # 将原始的提问也加入keys中  要利用set去重，防止query就在resuLt中
        keyswords = list(set(result + [query]))

        logger.info(f"抽取关键字完成：{keyswords}")

        return {"keywords": keyswords}
    except Exception as e:
        logger.error(f"抽取关键字失败：{str(e)}")
        raise
