from datetime import datetime
import json
import os  # 确保导入 os 模块
from ..files.config import config
from ..utils import get_file_path, update_file_status

class TranscriptManager:
    """识别结果管理类"""
    def __init__(self):
        self.transcripts_dir = config.transcripts_dir
        
    def save_result(self, file_id: str, result: dict):
        """保存识别结果"""
        try:
            file_dir = os.path.join(self.transcripts_dir, file_id)
            os.makedirs(file_dir, exist_ok=True)
            
            original_path = os.path.join(file_dir, "original.json")
            with open(original_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            metadata = {
                "created_at": datetime.now().isoformat(),
                "last_modified": datetime.now().isoformat(),
                "version_count": 0,
                "file_id": file_id,
                "status": "已完成"
            }
            metadata_path = os.path.join(file_dir, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 更新文件状态
            update_file_status(file_service, file_id, "已完成")
            
            return {"code": 200, "message": "success"}
            
        except Exception as e:
            print(f"Save recognition result error: {str(e)}")
            return {"code": 500, "message": f"保存识别结果失败: {str(e)}"}

    def get_file_info(self, file_id: str) -> dict:
        """获取文件信息，包括转写结果"""
        file_dir = os.path.join(self.transcripts_dir, file_id)
        
        transcripts = {}
        if os.path.exists(file_dir):
            print(f"Found transcript directory: {file_dir}")  # 添加调试日志
            
            original_path = os.path.join(file_dir, "original.json")
            if os.path.exists(original_path):
                print(f"Reading original.json from: {original_path}")  # 添加调试日志
                with open(original_path, "r", encoding="utf-8") as f:
                    original_data = json.load(f)
                    transcripts["original"] = original_data["data"]  # 直接获取 data 部分
                    print(f"Original data: {transcripts['original']}")  # 输出原始数据
                
            else:
                print(f"original.json not found at: {original_path}")  # 添加调试日志
                
            metadata_path = os.path.join(file_dir, "metadata.json")
            if os.path.exists(metadata_path):
                print(f"Reading metadata.json from: {metadata_path}")  # 添加调试日志
                with open(metadata_path, "r", encoding="utf-8") as f:
                    transcripts["metadata"] = json.load(f)
                    print(f"Metadata: {transcripts['metadata']}")  # 输出元数据
                
            else:
                print(f"metadata.json not found at: {metadata_path}")  # 添加调试日志
                
            current_path = os.path.join(file_dir, "current.json")
            if os.path.exists(current_path):
                print(f"Reading current.json from: {current_path}")  # 添加调试日志
                with open(current_path, "r", encoding="utf-8") as f:
                    transcripts["current"] = json.load(f)
                    print(f"Current data: {transcripts['current']}")  # 输出当前数据
                
            else:
                print(f"current.json not found at: {current_path}")  # 添加调试日志
        
        uploads_dir = config.uploads_dir
        
        result = {
            "id": file_id,
            "name": os.path.basename(file_id),
            "path": get_file_path(uploads_dir, file_id),
            "status": transcripts.get("metadata", {}).get("status", "未识别") if transcripts else "未识别",
            "transcripts": transcripts if transcripts else None,
            "recognition_result": None
        }
        
        print(f"Returning file info: {result}")  # 添加调试日志
        return result

# 创建全局实例
transcript_manager = TranscriptManager()
