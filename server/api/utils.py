import os
from typing import Optional, Tuple
from datetime import datetime
import json

def get_file_path(base_dir: str, file_id: str) -> str:
    """获取文件的完整路径
    Args:
        base_dir: 基础目录
        file_id: 文件ID
    Returns:
        str: 文件的完整路径
    """
    return os.path.join(base_dir, file_id)

def ensure_dir(dir_path: str) -> bool:
    """确保目录存在，如果不存在则创建
    Args:
        dir_path: 目录路径
    Returns:
        bool: 是否成功
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {dir_path}: {str(e)}")
        return False

def get_transcript_dir(base_dir: str, file_id: str) -> str:
    """获取转写结果目录路径
    Args:
        base_dir: 基础目录
        file_id: 文件ID
    Returns:
        str: 转写结果目录的完整路径
    """
    dir_path = os.path.join(base_dir, file_id)
    ensure_dir(dir_path)
    return dir_path

def parse_file_id(file_id: str) -> Tuple[str, str, str]:
    """解析文件ID，获取时间戳、语言和扩展名
    Args:
        file_id: 文件ID（如：20250109_141133_zh.wav）
    Returns:
        Tuple[str, str, str]: (timestamp, language, extension)
    """
    try:
        # 分离扩展名
        name, ext = os.path.splitext(file_id)
        # 分离语言标识
        parts = name.split('_')
        if len(parts) >= 3:
            timestamp = '_'.join(parts[:-1])  # 合并时间戳部分
            language = parts[-1]
        else:
            timestamp = name
            language = 'unknown'
        return timestamp, language, ext.lstrip('.')
    except Exception as e:
        print(f"Error parsing file_id {file_id}: {str(e)}")
        return file_id, 'unknown', ''

def generate_file_id(filename):
    """生成文件ID
    Args:
        filename: 原始文件名 (如: example.wav)
    Returns:
        str: 格式为 {timestamp}_{filename} 的文件ID
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # 如果文件名已经包含时间戳前缀，先去掉
    if '_' in filename:
        parts = filename.split('_')
        try:
            # 尝试解析第一部分是否为时间戳
            datetime.strptime(parts[0], '%Y%m%d')
            # 如果是时间戳，则使用剩余部分作为文件名
            filename = '_'.join(parts[2:])
        except ValueError:
            # 不是时间戳格式，使用完整文件名
            pass
            
    return f"{timestamp}_{filename}"

def safe_read_json(file_path: str, default_value=None):
    """安全地读取JSON文件
    Args:
        file_path: JSON文件路径
        default_value: 读取失败时的默认值
    Returns:
        读取的数据或默认值
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return default_value
    except Exception as e:
        print(f"Error reading JSON file {file_path}: {str(e)}")
        return default_value

def safe_write_json(file_path: str, data: dict, ensure_path: bool = True) -> bool:
    """安全地写入JSON文件
    Args:
        file_path: JSON文件路径
        data: 要写入的数据
        ensure_path: 是否确保目录存在
    Returns:
        bool: 是否写入成功
    """
    try:
        if ensure_path:
            ensure_dir(os.path.dirname(file_path))
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error writing JSON file {file_path}: {str(e)}")
        return False 