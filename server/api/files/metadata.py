import os
import json
from .config import config
from ..logger import get_logger

logger = get_logger(__name__)

class MetadataManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.metadata = {}
        return cls._instance
    
    def __init__(self):
        # 每次初始化都重新加载文件
        self.metadata_file = config.metadata_file
        self.metadata = self._load()  # 强制重新加载
    
    def _load(self):
        """加载元数据"""
        try:
            if os.path.exists(self.metadata_file):
                logger.debug(f"正在从 {self.metadata_file} 加载元数据")
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            logger.info(f"元数据文件不存在，将创建新的元数据")
            return {}
        except Exception as e:
            logger.error(f"加载元数据失败: {e}")
            return {}
    
    def save(self):
        """保存元数据"""
        try:
            logger.info(f"保存元数据文件")
            logger.debug(f"保存路径: {self.metadata_file}")
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
            logger.debug(f"元数据文件保存成功，包含 {len(self.metadata)} 条记录")
        except Exception as e:
            logger.error(f"保存元数据失败: {e}")
    
    def update(self, filename, data):
        """更新元数据"""
        # 每次更新前都重新加载
        self.metadata = self._load()  
        
        logger.info(f"更新元数据: {filename}")
        logger.debug(f"更新内容: {data}")
        
        self.metadata[filename] = data
        self.save()
        logger.debug("元数据更新完成")
    
    def delete(self, filename):
        """删除元数据"""
        if filename in self.metadata:
            logger.info(f"删除元数据: {filename}")
            del self.metadata[filename]
            self.save()
            # 删除后重新加载确保内存与文件同步
            self.reload()
        else:
            logger.debug(f"尝试删除不存在的元数据: {filename}")
    
    def get(self, filename):
        """获取元数据"""
        logger.debug(f"获取元数据: {filename}")
        return self.metadata.get(filename, {}) 
    
    def reload(self):
        """重新从文件加载元数据"""
        logger.info("重新加载元数据文件")
        self.metadata = self._load()
        logger.debug(f"重新加载后的元数据条目数: {len(self.metadata)}")
    
    def get_by_file_id(self, file_id: str) -> dict:
        """通过 file_id 获取元数据"""
        logger.debug(f"通过 file_id 查找元数据: {file_id}")
        # 直接搜索包含 file_id 的键
        for key in self.metadata:
            if file_id in key:  # 只要键中包含 file_id 就匹配
                logger.debug(f"找到匹配的元数据: {key}")
                return self.metadata.get(key, {})
        logger.info(f"未找到 file_id 为 {file_id} 的元数据")
        return {}