import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime
from app.core.config import get_logging_config

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 日志文件路径
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = LOG_DIR / f"fastapi_{datetime.now().strftime('%Y-%m-%d')}.log"

# 配置日志
logger.configure(**get_logging_config())

# 导出logger实例
get_logger = logger.bind 