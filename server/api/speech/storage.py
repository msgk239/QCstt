from datetime import datetime
import os
from ..files.config import config
from ..utils import get_transcript_dir, safe_read_json, safe_write_json
from ..logger import get_logger

logger = get_logger(__name__)

class TranscriptManager:
    """转写结果存储模块"""
    def __init__(self):
        self.transcripts_dir = config.transcripts_dir
        
    def save_result(self, file_id: str, result: dict) -> bool:
        """保存识别结果"""
        try:
            logger.info(f"开始保存转写结果: {file_id}")
            file_dir = get_transcript_dir(self.transcripts_dir, file_id)
            
            # 保存原始识别结果
            original_path = os.path.join(file_dir, "original.json")
            if not safe_write_json(original_path, result):
                logger.error(f"保存原始识别结果失败: {file_id}")
                return False
            
            # 保存元数据
            metadata = {
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version_count": 0,
                "file_id": file_id,
                "status": "已完成"
            }
            metadata_path = os.path.join(file_dir, "metadata.json")
            return safe_write_json(metadata_path, metadata)
            
        except Exception as e:
            logger.error(f"保存识别结果出错: {str(e)}")
            return False

    def get_transcript(self, file_id: str) -> dict:
        """获取转写结果"""
        file_dir = get_transcript_dir(self.transcripts_dir, file_id)
        logger.info(f"开始获取转写结果, 文件ID: {file_id}")
        logger.debug(f"转写目录: {file_dir}")
        result = {}
        
        # 读取所有相关文件
        file_types = {
            "original": "original.json",
            "metadata": "metadata.json",
            "current": "current.json"
        }
        
        for key, filename in file_types.items():
            file_path = os.path.join(file_dir, filename)
            logger.debug(f"检查文件: {file_path}, 是否存在: {os.path.exists(file_path)}")
            
            data = safe_read_json(file_path)
            if data:
                logger.debug(f"成功读取 {key} 数据")
                result[key] = data
            else:
                logger.info(f"未找到 {key} 数据")
                
        logger.debug("转写结果获取完成")
        return result if result else None

    def delete_transcript(self, file_id: str) -> bool:
        """删除转写结果"""
        try:
            file_dir = os.path.join(self.transcripts_dir, file_id)
            if os.path.exists(file_dir):
                import shutil
                shutil.rmtree(file_dir)
                logger.info(f"成功删除转写结果: {file_id}")
            return True
        except Exception as e:
            logger.error(f"删除转写结果出错: {str(e)}")
            return False

    def get_metadata(self, file_id: str) -> dict:
        """获取转写元数据"""
        file_dir = get_transcript_dir(self.transcripts_dir, file_id)
        metadata_path = os.path.join(file_dir, "metadata.json")
        logger.debug(f"获取元数据, 路径: {metadata_path}, 是否存在: {os.path.exists(metadata_path)}")
        metadata = safe_read_json(metadata_path)
        logger.debug(f"元数据内容: {metadata}")
        return metadata

# 创建全局实例
transcript_manager = TranscriptManager()
