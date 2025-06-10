import os
import sys
from loguru import logger
from pathlib import Path
from datetime import datetime

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 日志文件路径
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = LOG_DIR / f"fastapi_{datetime.now().strftime('%Y-%m-%d')}.log"

# 日志配置
config = {
    "handlers": [
        # 控制台输出
        {
            "sink": sys.stdout,
            "format": os.getenv('LOG_FORMAT', "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"),
            "level": os.getenv('LOG_LEVEL', "INFO"),
        },
        # 文件输出
        {
            "sink": str(LOG_FILE),
            "format": os.getenv('LOG_FORMAT', "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"),
            "level": os.getenv('LOG_LEVEL', "INFO"),
            "rotation": os.getenv('LOG_ROTATION', "500 MB"),
            "retention": os.getenv('LOG_RETENTION', "30 days"),
            "compression": os.getenv('LOG_COMPRESSION', "zip"),
            "encoding": "utf-8"
        },
    ]
}

# 移除默认的处理器
logger.remove()

# 使用配置添加处理器
for handler in config["handlers"]:
    logger.add(**handler)

def get_logger(name: str):
    """
    获取logger实例
    :param name: logger名称
    :return: logger实例
    """
    return logger.bind(name=name)