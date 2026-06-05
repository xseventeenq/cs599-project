"""
UAV-Mission-Agent 配置管理模块

管理项目的配置设置，包括环境变量加载、LLM配置、数据库配置等。
"""

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv(*args, **kwargs):
        return False


class Config:
    """项目配置类"""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            env_file: 环境变量文件路径，默认为项目根目录下的 .env
        """
        if env_file is None:
            # 默认加载项目根目录下的 .env 文件
            project_root = Path(__file__).parent.parent
            env_file = project_root / ".env"
        
        # 加载环境变量
        load_dotenv(env_file)
        
        # 初始化配置
        self._init_llm_config()
        self._init_vector_db_config()
        self._init_logging_config()
        self._init_streamlit_config()
        self._init_evaluation_config()
    
    def _init_llm_config(self):
        """初始化LLM配置"""
        self.llm = {
            "provider": "deepseek",
            "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "base_url": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
            "model": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 2048,
        }
    
    def _init_vector_db_config(self):
        """初始化向量数据库配置"""
        self.vector_db = {
            "provider": "faiss",  # 或 "chroma"
            "path": os.getenv("VECTOR_DB_PATH", "./data/vector_db"),
            "dimension": 1536,  # 嵌入向量维度
        }
    
    def _init_logging_config(self):
        """初始化日志配置"""
        self.logging = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "file": os.getenv("LOG_FILE", "./data/logs/app.log"),
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
    
    def _init_streamlit_config(self):
        """初始化Streamlit配置"""
        self.streamlit = {
            "port": int(os.getenv("STREAMLIT_SERVER_PORT", "8501")),
            "address": os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost"),
        }
    
    def _init_evaluation_config(self):
        """初始化评估配置"""
        self.evaluation = {
            "output_dir": os.getenv("EVALUATION_OUTPUT_DIR", "./data/evaluation"),
            "metrics": ["success_rate", "total_cost", "average_risk"],
        }
    
    def get_llm_config(self) -> dict:
        """获取LLM配置"""
        return self.llm.copy()
    
    def get_vector_db_config(self) -> dict:
        """获取向量数据库配置"""
        return self.vector_db.copy()
    
    def get_logging_config(self) -> dict:
        """获取日志配置"""
        return self.logging.copy()
    
    def get_streamlit_config(self) -> dict:
        """获取Streamlit配置"""
        return self.streamlit.copy()
    
    def get_evaluation_config(self) -> dict:
        """获取评估配置"""
        return self.evaluation.copy()
    
    def validate(self) -> bool:
        """验证配置是否完整"""
        errors = []
        
        if not self.llm["api_key"]:
            errors.append("DEEPSEEK_API_KEY 未设置")
        
        # 验证目录是否存在，如果不存在则创建
        for dir_path in [self.vector_db["path"], self.evaluation["output_dir"], 
                         os.path.dirname(self.logging["file"])]:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        if errors:
            for error in errors:
                print(f"配置错误: {error}")
            return False
        
        return True


# 全局配置实例
_config = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = Config()
    return _config


def init_config(env_file: Optional[str] = None) -> Config:
    """初始化配置"""
    global _config
    _config = Config(env_file)
    return _config