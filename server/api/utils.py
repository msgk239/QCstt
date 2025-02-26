import os
from typing import Optional, Tuple
from datetime import datetime
import json
import re
from .logger import get_logger

logger = get_logger(__name__)

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不合法字符
    Args:
        filename: 原始文件名
    Returns:
        str: 清理后的文件名
    """
    # 保留中文、英文、数字、下划线、连字符
    cleaned = re.sub(r'[^\w\-\u4e00-\u9fff]', '_', filename)
    # 移除连续的下划线
    cleaned = re.sub(r'_+', '_', cleaned)
    # 移除首尾的下划线
    cleaned = cleaned.strip('_')
    return cleaned if cleaned else 'unnamed'

def generate_target_filename(original_filename: str) -> tuple:
    """生成目标文件名，并返回相关的文件名信息
    Args:
        original_filename: 原始文件名
    Returns:
        tuple: (
            target_filename,  # 完整的目标文件名（带时间戳和扩展名）
            cleaned_name,     # 清理后的显示名称（不带扩展名）
            cleaned_full_name,# 清理后的完整文件名（带扩展名）
            ext              # 文件扩展名（带点号）
        )
    """
    name, ext = os.path.splitext(original_filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    cleaned_name = sanitize_filename(name)
    cleaned_full_name = f"{cleaned_name}{ext}"
    target_filename = f"{timestamp}_{cleaned_name}{ext}"
    return target_filename, cleaned_name, cleaned_full_name, ext

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
        logger.error(f"创建目录失败 {dir_path}: {str(e)}")
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
            dir_path = os.path.dirname(file_path)
            logger.debug(f"确保目录存在: {dir_path}")
            if not ensure_dir(dir_path):
                logger.error(f"创建目录失败: {dir_path}")
                return False
        
        logger.debug(f"开始写入文件: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"文件写入成功: {file_path}")
        return True
    except Exception as e:
        logger.error(f"写入JSON文件失败: {file_path}", exc_info=True)
        logger.debug(f"错误详情: {str(e)}")
        logger.debug(f"文件路径: {file_path}")
        logger.debug(f"目录是否存在: {os.path.exists(os.path.dirname(file_path))}")
        logger.debug(f"目录权限: {oct(os.stat(os.path.dirname(file_path)).st_mode)[-3:]}")
        return False

def get_audio_metadata(file_path: str, metadata_path: str) -> dict:
    """获取音频文件的元数据
    Args:
        file_path: 音频文件路径
        metadata_path: metadata.json 文件路径
    Returns:
        dict: 包含音频时长等信息的元数据
    """
    try:
        metadata = safe_read_json(metadata_path, {})
        
        filename = os.path.basename(file_path)
        logger.debug(f"查找音频元数据 - 文件名: {filename}")
        logger.debug(f"当前元数据内容: {metadata}")
        
        file_metadata = metadata.get(filename, {})
        if not file_metadata:
            simple_name = '_'.join(filename.split('_')[2:]) if '_' in filename else filename
            file_metadata = metadata.get(simple_name, {})
            logger.debug(f"尝试简化文件名匹配: {simple_name}")
        
        if file_metadata:
            logger.info(f"找到音频元数据: {file_metadata}")
            return file_metadata
        else:
            logger.warning(f"未找到音频元数据: {filename}")
            return {
                "duration": 0,
                "duration_str": "00:00"
            }
            
    except Exception as e:
        logger.error(f"获取音频元数据失败: {str(e)}")
        return {
            "duration": 0,
            "duration_str": "00:00"
        }