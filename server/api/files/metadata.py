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
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"加载元数据失败: {e}")
            return {}
    
    def save(self):
        """保存元数据"""
        try:
            logger.info(f"=== 开始保存元数据文件 ===")
            logger.debug(f"保存路径: {self.metadata_file}")
            logger.debug(f"保存内容: {self.metadata}")
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
                
            logger.info("元数据文件保存成功")
        except Exception as e:
            logger.error(f"保存元数据失败: {e}")
    
    def update(self, filename, data):
        """更新元数据"""
        # 每次更新前都重新加载
        self.metadata = self._load()  
        
        logger.info(f"=== 开始更新元数据 ===")
        logger.debug(f"文件名: {filename}")
        logger.debug(f"更新数据: {data}")
        
        self.metadata[filename] = data
        self.save()
        logger.info("元数据更新完成")
    
    def delete(self, filename):
        """删除元数据"""
        if filename in self.metadata:
            del self.metadata[filename]
            self.save()
            # 删除后重新加载确保内存与文件同步
            self.reload()
    
    def get(self, filename):
        """获取元数据"""
        return self.metadata.get(filename, {}) 
    
    def reload(self):
        """重新从文件加载元数据"""
        logger.info("=== 重新加载元数据文件 ===")
        self.metadata = self._load()
        logger.debug(f"重新加载后的元数据内容: {self.metadata}")
 