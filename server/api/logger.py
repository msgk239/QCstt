import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Any
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.status import Status
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich import print
import json

# 创建控制台实例时配置
console = Console(
    force_terminal=True,
    color_system="auto",
    width=None,
    tab_size=4,
    record=False,
    markup=True
)

# 配置异常处理
install(
    console=console,
    width=None,           # 自动宽度
    extra_lines=0,        # 不显示额外的上下文行
    theme=None,           # 使用简单主题
    show_locals=False,    # 不显示本地变量
    max_frames=1,          # 只显示最后一帧
    suppress=[           # 添加这个参数来抑制特定框架的堆栈跟踪
        "uvicorn",
        "fastapi",
        "starlette",
        "pydantic"
    ]
)

# 配置日志处理器
handler = RichHandler(
    console=console,
    rich_tracebacks=True,
    omit_repeated_times=True,
    show_path=False,
    enable_link_path=False,
    markup=True,
    show_time=False,
    show_level=True,
    tracebacks_show_locals=False,
    tracebacks_extra_lines=0,
    tracebacks_theme=None,
    tracebacks_word_wrap=True
)

class LogConfig:
    """日志配置类"""
    # 修改日志级别为 DEBUG
    LOG_LEVEL = logging.DEBUG  # 显示所有日志信息
    LOG_DIR = os.path.join("server", "logs")  # 修改为 server/logs
    LOG_FILENAME = "app.log"  # 主日志文件
    ERROR_FILENAME = "error.log"  # 错误日志文件
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5
    DEBUG = True
    
    # 添加详细日志格式
    DETAILED_FILE_FORMAT = '%(asctime)s [%(levelname)s] %(pathname)s:%(lineno)d:\n%(message)s'
    # 保持控制台格式简短
    CONSOLE_FORMAT = "%(levelname)s: %(message)s"
    
    # 文件日志格式也简化
    FILE_FORMAT = '%(asctime)s %(levelname)s: %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # FastAPI 相关配置
    FASTAPI_DEBUG = True
    FASTAPI_LOG_LEVEL = logging.DEBUG

class JsonFormatter(logging.Formatter):
    """自定义 JSON 格式化器"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def format(self, record: logging.LogRecord) -> str:
        # 先获取标准格式化的消息
        formatted = super().format(record)
        
        try:
            # 尝试在完整消息中查找 JSON 内容
            message = record.getMessage()
            if isinstance(message, str) and (message.startswith('{') or message.startswith('[')):
                parsed = json.loads(message)
                # 美化 JSON 输出，使用4个空格缩进
                formatted_json = json.dumps(parsed, indent=4, ensure_ascii=False)
                # 替换原始消息，保持其他格式信息
                formatted = formatted.replace(message, f"\n{formatted_json}")
        except (json.JSONDecodeError, TypeError):
            pass
        
        return formatted

class CustomFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            fmt='%(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 添加重复日志检测
        self.last_log = None
        self.repeat_count = 0
        
    def format(self, record):
        # 检查是否是重复日志
        current_log = f"{record.levelname}{record.getMessage()}"
        
        if current_log == self.last_log:
            self.repeat_count += 1
            return None  # 跳过重复日志
            
        self.last_log = current_log
        self.repeat_count = 0
        
        return super().format(record)

class JsonFilter(logging.Filter):
    """过滤 JSON 格式的日志，使其不在终端显示"""
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        # 如果是 JSON 格式，返回 False 表示不显示
        return not (isinstance(message, str) and 
                   (message.startswith('{') or message.startswith('[')))

class Logger:
    """日志管理类"""
    _instance: Optional[logging.Logger] = None
    _console = Console()  # rich console 实例
    
    @classmethod
    def setup(cls) -> logging.Logger:
        """配置并返回日志记录器"""
        if cls._instance is not None:
            return cls._instance
            
        # 确保日志目录存在
        if not os.path.exists(LogConfig.LOG_DIR):
            os.makedirs(LogConfig.LOG_DIR)
        
        # 获取根日志记录器
        logger = logging.getLogger()
        
        # 如果已经有处理器，先清除
        if logger.handlers:
            logger.handlers.clear()
        
        # 设置日志级别
        logger.setLevel(logging.DEBUG if LogConfig.DEBUG else logging.INFO)
        
        # 修改文件日志格式化器为自定义的 JSON 格式化器
        file_formatter = JsonFormatter(
            LogConfig.DETAILED_FILE_FORMAT,
            datefmt=LogConfig.DATE_FORMAT
        )
        
        # 1. 使用 RichHandler 替代普通的 StreamHandler
        console = Console(
            force_terminal=True,
        )
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
            tracebacks_extra_lines=0,
            tracebacks_theme=None,
            tracebacks_width=100,    # 限制宽度
            tracebacks_suppress=[    # 在这里也添加抑制配置
                "uvicorn",
                "fastapi",
                "starlette",
                "pydantic"
            ],
            show_time=False,
            show_path=False,
            markup=True,
            enable_link_path=False,
            show_level=True,
            omit_repeated_times=True
        )
        console_handler.addFilter(JsonFilter())  # 添加 JSON 过滤器
        console_handler.setFormatter(logging.Formatter(LogConfig.CONSOLE_FORMAT))
        console_handler.setLevel(logging.DEBUG)  # 终端显示所有级别
        logger.addHandler(console_handler)
        
        # 2. 主日志文件处理器
        file_handler = RotatingFileHandler(
            os.path.join(LogConfig.LOG_DIR, LogConfig.LOG_FILENAME),
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # 3. 错误日志文件处理器
        error_handler = RotatingFileHandler(
            os.path.join(LogConfig.LOG_DIR, LogConfig.ERROR_FILENAME),
            maxBytes=LogConfig.MAX_BYTES,
            backupCount=LogConfig.BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        # 配置第三方库的日志级别
        logging.getLogger("uvicorn").setLevel(logging.INFO)
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
        logging.getLogger("python_multipart").setLevel(logging.WARNING)
        logging.getLogger("fastapi").setLevel(LogConfig.FASTAPI_LOG_LEVEL)
        
        # 添加请求处理器
        cls.setup_request_handlers(logger)
        
        cls._instance = logger
        return logger
    
    @classmethod
    def get_logger(cls, name: str = None) -> logging.Logger:
        """获取指定名称的日志记录器"""
        if cls._instance is None:
            cls.setup()
        
        if name:
            return logging.getLogger(name)
        return cls._instance
    
    @staticmethod
    def setup_request_handlers(logger):
        """配置请求处理相关的日志记录"""
        def log_request(request, response=None, error=None):
            extra = {
                'method': request.method,
                'url': str(request.url),
                'client': request.client.host if request.client else 'unknown',
                'status_code': getattr(response, 'status_code', None)
            }
            
            if error:
                logger.error(f"请求处理错误: {str(error)}", extra=extra)
            else:
                logger.info(f"请求处理完成", extra=extra)
                
        return log_request
    
    @classmethod
    def progress(cls, total: int, description: str = "Processing") -> Progress:
        """创建进度条"""
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            "•",
            "{task.completed}/{task.total}",
            console=cls._console
        )
        progress.add_task(description, total=total)
        return progress
    
    @classmethod
    def status(cls, message: str) -> Status:
        """创建状态显示"""
        return Status(message, console=cls._console)
    
    @classmethod
    def table(cls, title: str = None) -> Table:
        """创建表格"""
        return Table(title=title, show_header=True, header_style="bold magenta")
    
    @classmethod
    def tree(cls, label: str) -> Tree:
        """创建树形结构"""
        return Tree(label)

# 为方便使用，提供快捷方法
def get_logger(name: str = None) -> logging.Logger:
    """获取日志记录器的快捷方法
    Args:
        name: 日志记录器名称，通常使用 __name__
    Returns:
        logging.Logger: 日志记录器实例
    """
    return Logger.get_logger(name) 