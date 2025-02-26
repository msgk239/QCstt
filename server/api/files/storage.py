import os
import json
from datetime import datetime
from ..logger import get_logger
logger = get_logger(__name__)

class File:
    """文件模型类"""
    def __init__(self, id, name, speech_type=None):
        self.id = id
        self.name = name
        self.speech_type = speech_type

def ensure_dir(dir_path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(dir_path):
        logger.debug(f"目录不存在，创建目录: {dir_path}")
        os.makedirs(dir_path)
    else:
        logger.debug(f"目录已存在: {dir_path}")

def safe_write_json(file_path, data):
    """安全地写入 JSON 文件"""
    try:
        logger.debug(f"开始写入JSON文件: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"JSON文件写入成功: {file_path}")
        return True
    except Exception as e:
        logger.error(f"写入JSON文件失败: {str(e)}, 文件路径: {file_path}")
        return False

class FileStorage:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        logger.info(f"初始化文件存储，基础目录: {base_dir}")
        ensure_dir(base_dir)
        
    def save_file(self, file_content, file_id, metadata=None):
        """保存文件
        Args:
            file_content: 文件内容
            file_id: 文件ID 
            metadata: 文件元数据，包含原始文件名等信息
        """
        try:
            logger.info(f"开始保存文件: {file_id}")
            # 确保文件名格式正确
            if not self._validate_file_id(file_id):
                logger.error(f"无效的文件ID: {file_id}")
                return {
                    "code": 400,
                    "message": "文件ID格式不正确"
                }
            
            # 构建完整路径
            file_path = os.path.join(self.base_dir, file_id)
            logger.debug(f"文件完整路径: {file_path}")
            
            # 保存文件
            logger.debug(f"写入文件内容，大小: {len(file_content)} 字节")
            with open(file_path, 'wb') as f:
                f.write(file_content)
                
            # 保存元数据
            if metadata:
                logger.debug(f"保存文件元数据: {metadata}")
                self._save_metadata(file_id, metadata)
            else:
                logger.debug("无元数据需要保存")
                
            logger.info(f"文件保存成功: {file_id}")
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "file_id": file_id,
                    "path": file_path
                }
            }
            
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}, 文件ID: {file_id}")
            return {
                "code": 500,
                "message": f"保存文件失败: {str(e)}"
            }
            
    def _validate_file_id(self, file_id):
        """验证文件ID格式
        格式: YYYYMMDD_HHMMSS_filename.wav
        """
        try:
            logger.debug(f"验证文件ID格式: {file_id}")
            # 检查基本格式
            if not file_id or '_' not in file_id:
                logger.debug(f"文件ID格式不正确: {file_id}")
                return False
            
            # 分离时间戳和文件名
            timestamp = '_'.join(file_id.split('_')[:2])  # 获取完整时间戳 YYYYMMDD_HHMMSS
            logger.debug(f"提取的时间戳: {timestamp}")
            
            # 验证时间戳格式
            datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            logger.debug(f"文件ID格式验证通过: {file_id}")
            
            return True
            
        except ValueError:
            logger.debug(f"时间戳格式无效: {file_id}")
            return False
            
    def _save_metadata(self, file_id, metadata):
        """保存文件元数据"""
        metadata_path = os.path.join(self.base_dir, f"{file_id}.meta.json")
        logger.debug(f"保存元数据到: {metadata_path}")
        safe_write_json(metadata_path, metadata) 