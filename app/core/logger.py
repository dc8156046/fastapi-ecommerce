import logging
import sys
from pathlib import Path
from loguru import logger
from datetime import datetime

# 创建日志目录
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
log_file = LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"

# 配置 loguru
config = {
    "handlers": [
        {
            "sink": sys.stdout,
            "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            "level": "INFO",
        },
        {
            "sink": str(log_file),
            "format": "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            "level": "DEBUG",
            "rotation": "00:00",  # 每天轮换
            "retention": "30 days",  # 保留30天
            "compression": "zip",  # 压缩旧日志
        },
    ],
}

# 移除默认处理器
logger.remove()

# 添加新的处理器
for handler in config["handlers"]:
    logger.add(**handler)

# 设置日志级别
logger.level("INFO")

# 添加上下文信息
logger = logger.bind(service="membership-system")


class InterceptHandler(logging.Handler):
    """
    将标准库的日志重定向到 loguru
    """

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# 配置标准库日志
logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

# 配置第三方库的日志
for _log in ["uvicorn", "uvicorn.error", "fastapi"]:
    _logger = logging.getLogger(_log)
    _logger.handlers = [InterceptHandler()]

# 导出 logger
__all__ = ["logger"]
