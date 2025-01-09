import os
import json
from .config import config

class MetadataManager:
    """元数据管理类"""
    def __init__(self):
        self.metadata_file = config.metadata_file
        self.metadata = self._load()
    
    def _load(self):
        """加载元数据"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"加载元数据失败: {e}")
            return {}
    
    def save(self):
        """保存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存元数据失败: {e}")
    
    def update(self, filename, data):
        """更新元数据"""
        self.metadata[filename] = data
        self.save()
    
    def delete(self, filename):
        """删除元数据"""
        if filename in self.metadata:
            del self.metadata[filename]
            self.save()
    
    def get(self, filename):
        """获取元数据"""
        return self.metadata.get(filename, {}) 