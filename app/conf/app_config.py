import os
from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf


_project_root = Path(__file__).parents[2]
_env_path = _project_root / ".env"


def _load_local_env() -> None:
    if not _env_path.exists():
        return

    for raw_line in _env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_local_env()

_required_env_vars = ("INSIGHTQUERY_DB_PASSWORD", "INSIGHTQUERY_LLM_API_KEY")
_missing_env_vars = [name for name in _required_env_vars if not os.getenv(name)]
if _missing_env_vars:
    raise RuntimeError(
        "Missing required environment variables: " + ", ".join(_missing_env_vars)
    )

# ======日志配置类型=========
# 定义数据的模型
@dataclass
class File:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str
@dataclass
class Console:
    enable: bool
    level: str
@dataclass
class LoggingConfig:
    file: File
    console: Console

# ==================== database配置模型 ====================

@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

# ==================== Qdrant 配置模型 ====================

@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int


# ==================== Embedding 配置模型 ====================

@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str


# ==================== ES 配置模型 ====================

@dataclass
class ESConfig:
    host: str
    port: int
    index_name: str


# ==================== LLM 配置模型 ====================

@dataclass
class LLMConfig:
    model_name: str
    api_key: str


# ==================== 应用总配置模型 ====================

@dataclass
class AppConfig:
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig

# yaml配置文件的路径
_yaml_path = _project_root / "conf/app_config.yaml"

# 加载yaml文件
_yaml_data = OmegaConf.load(_yaml_path)

# 将_yaml_data转换为指定类型AppConfig的对象
app_config:AppConfig = OmegaConf.to_object(OmegaConf.merge(AppConfig, _yaml_data))

if __name__ == '__main__':
    print(app_config, type(app_config))
    print(app_config.logging.file.level)
