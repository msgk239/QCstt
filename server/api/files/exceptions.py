class FileServiceError(Exception):
    """文件服务异常基类"""
    pass

class FileNotFoundError(FileServiceError):
    """文件不存在异常"""
    pass 