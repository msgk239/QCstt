from datetime import datetime
import os
import json
from ..files.config import config
from ..files.service import file_service

class TranscriptManager:
    """识别结果管理类"""
    def __init__(self):
        self.transcripts_dir = config.transcripts_dir
        
    def save_result(self, file_id: str, result: dict):
        """保存识别结果"""
        try:
            # 创建文件专属目录
            file_dir = os.path.join(self.transcripts_dir, file_id)
            os.makedirs(file_dir, exist_ok=True)
            
            # 保存原始识别结果
            original_path = os.path.join(file_dir, "original.json")
            with open(original_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 保存元数据
            metadata = {
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version_count": 0,
                "file_id": file_id,
                "status": "completed"
            }
            metadata_path = os.path.join(file_dir, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 更新文件状态
            file_service.update_file_status(file_id, "已完成")
            
            return {"code": 200, "message": "success"}
            
        except Exception as e:
            print(f"Save recognition result error: {str(e)}")
            return {"code": 500, "message": f"保存识别结果失败: {str(e)}"}

# 创建全局实例
transcript_manager = TranscriptManager()
