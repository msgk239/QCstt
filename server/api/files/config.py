import os

class FileConfig:
    """文件服务配置类"""
    def __init__(self):
        # 获取项目根目录
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # 设置存储根目录
        self.storage_root = os.path.join(self.root_dir, "storage")
        self.uploads_dir = os.path.join(self.storage_root, "uploads")
        self.audio_dir = os.path.join(self.uploads_dir, "audio")
        self.trash_dir = os.path.join(self.storage_root, "trash")
        self.metadata_file = os.path.join(self.storage_root, "metadata.json")
        
        # 添加识别结果存储目录
        self.transcripts_dir = os.path.join(self.storage_root, "transcripts")
        
        # 确保目录存在
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.trash_dir, exist_ok=True)
        os.makedirs(self.transcripts_dir, exist_ok=True)

# 创建全局配置实例
config = FileConfig() 