import logging
from typing import Optional, Any
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.status import Status
from rich.table import Table
from rich.tree import Tree
import json
import inspect

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
    # 日志级别配置
    # DEBUG: 显示所有日志（开发调试用）
    # INFO: 显示一般信息
    # WARNING: 只显示警告和错误（生产环境推荐）
    # ERROR: 只显示错误
    LOG_LEVEL = logging.DEBUG  # 改为调试级别
    
    # 调试模式开关
    # True: 显示详细日志（开发环境）
    # False: 精简日志（生产环境）
    DEBUG = True  # 改为调试模式
    
    # 控制台日志格式
    CONSOLE_FORMAT = "%(levelname)s: %(message)s"
    
    # FastAPI 配置
    # True: 显示详细的API调试信息
    # False: 关闭API调试信息（生产环境推荐）
    FASTAPI_DEBUG = True  # 改为调试模式
    
    # FastAPI 日志级别
    # logging.DEBUG: 显示所有API相关日志
    # logging.INFO: 显示一般API信息
    # logging.WARNING: 只显示API警告和错误（生产环境推荐）
    FASTAPI_LOG_LEVEL = logging.DEBUG  # 改为调试级别
    
    # 入口文件配置
    ENTRY_LOG_LEVELS = {
        "server.api.app": logging.DEBUG,      # 从 app.py 启动时使用 DEBUG 级别
        "server.api.QCstt": logging.INFO,     # 从 QCstt.py 启动时使用 INFO 级别
    }

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
    _instance = None
    _entry_point = None
    
    @classmethod
    def set_entry_point(cls, entry_point: str):
        """设置入口文件模块名并更新根日志级别"""
        frame = inspect.currentframe()
        while frame:
            if frame.f_globals.get('__name__') == '__main__':
                cls._entry_point = entry_point
                # 获取新的日志级别
                log_level = LogConfig.ENTRY_LOG_LEVELS.get(entry_point, LogConfig.LOG_LEVEL)
                # 设置根日志记录器的级别
                logging.getLogger().setLevel(log_level)
                
                # 同时设置第三方库的日志级别
                for logger_name in [
                    "uvicorn",
                    "uvicorn.access",
                    "python_multipart",
                    "fastapi"
                ]:
                    logging.getLogger(logger_name).setLevel(log_level)
                break
            frame = frame.f_back
    
    @classmethod
    def get_logger(cls, name: str = None) -> logging.Logger:
        """获取日志记录器
        
        如果系统还没有初始化，会自动调用 setup() 进行初始化。
        所有返回的 logger 都会继承根日志记录器的级别。
        
        Args:
            name: logger 的名称，如果不指定则返回根日志记录器
            
        Returns:
            logging.Logger: 日志记录器实例
        """
        # 确保系统已初始化
        if not cls._instance:
            cls.setup()
        # 返回指定名称的 logger 或根日志记录器
        return logging.getLogger(name) if name else cls._instance

    @classmethod
    def setup(cls) -> logging.Logger:
        """配置并返回根日志记录器"""
        # 如果已经初始化过，直接返回实例
        if cls._instance:
            return cls._instance
            
        # 获取根日志记录器
        logger = logging.getLogger()
        
        # 如果已经有处理器，先清除
        if logger.handlers:
            logger.handlers.clear()
        
        # 根据入口点设置日志级别
        log_level = LogConfig.ENTRY_LOG_LEVELS.get(cls._entry_point, LogConfig.LOG_LEVEL)
        logger.setLevel(log_level)
        
        # 控制台处理器配置...
        console_handler = RichHandler(
            console=console,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
            tracebacks_extra_lines=0,
            tracebacks_theme=None,
            tracebacks_width=100,
            tracebacks_suppress=[
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
        console_handler.addFilter(JsonFilter())
        console_handler.setFormatter(logging.Formatter(LogConfig.CONSOLE_FORMAT))
        console_handler.setLevel(log_level)  # 使用相同的日志级别
        logger.addHandler(console_handler)
        
        # 第三方库日志级别配置
        third_party_loggers = [
            "uvicorn",
            "uvicorn.access",
            "python_multipart",
            "fastapi"
        ]
        
        # 根据入口点设置第三方库的日志级别
        for logger_name in third_party_loggers:
            third_party_logger = logging.getLogger(logger_name)
            third_party_logger.setLevel(log_level)
        
        cls._instance = logger
        return logger
    
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
            console=console
        )
        progress.add_task(description, total=total)
        return progress
    
    @classmethod
    def status(cls, message: str) -> Status:
        """创建状态显示"""
        return Status(message, console=console)
    
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