import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 日志文件路径
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = LOG_DIR / f"fastapi_{datetime.now().strftime('%Y-%m-%d')}.log"

# 配置日志
logger.configure(
    {
        "handlers": [
            # 控制台输出
            {
                "sink": "sys.stdout",
                "format": os.getenv("LOG_FORMAT"),
                "level": os.getenv("LOG_LEVEL"),
            },
            # 文件输出
            {
                "sink": str(os.getenv("LOG_DIR") / f"fastapi_{os.getenv("LOG_LEVEL").lower()}.log"),
                "format": os.getenv("LOG_FORMAT"),
                "level": os.getenv("LOG_LEVEL"),
                "rotation": os.getenv("LOG_ROTATION"),
                "retention": os.getenv("LOG_RETENTION"),
                "compression": os.getenv("LOG_COMPRESSION"),
            },
        ],
    }
)

def get_logger(name: str):
    """
    获取logger实例
    :param name: logger名称
    :return: logger实例
    """
    return logger.bind(name=name) 