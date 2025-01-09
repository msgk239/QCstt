from datetime import datetime
import os
from ..files.config import config
from ..utils import get_transcript_dir, safe_read_json, safe_write_json

class TranscriptManager:
    """转写结果存储模块"""
    def __init__(self):
        self.transcripts_dir = config.transcripts_dir
        
    def save_result(self, file_id: str, result: dict) -> bool:
        """保存识别结果"""
        try:
            file_dir = get_transcript_dir(self.transcripts_dir, file_id)
            
            # 保存原始识别结果
            original_path = os.path.join(file_dir, "original.json")
            if not safe_write_json(original_path, result):
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
            print(f"Save recognition result error: {str(e)}")
            return False

    def get_transcript(self, file_id: str) -> dict:
        """获取转写结果"""
        file_dir = get_transcript_dir(self.transcripts_dir, file_id)
        print(f"\n=== 开始获取转写结果 ===")
        print(f"文件ID: {file_id}")
        print(f"转写目录: {file_dir}")
        result = {}
        
        # 读取所有相关文件
        file_types = {
            "original": "original.json",
            "metadata": "metadata.json",
            "current": "current.json"
        }
        
        for key, filename in file_types.items():
            file_path = os.path.join(file_dir, filename)
            print(f"\n检查文件: {file_path}")
            print(f"文件是否存在: {os.path.exists(file_path)}")
            
            data = safe_read_json(file_path)
            if data:
                print(f"成功读取 {key} 数据")
                # 如果是original文件，尝试处理可能的嵌套结构
                if key == "original" and isinstance(data, dict):
                    print(f"Original数据结构: {type(data)}")
                    # 如果有data字段，直接使用其内容
                    if "data" in data:
                        result[key] = data["data"]
                        print("使用data字段内容")
                    # 否则使用整个数据
                    else:
                        result[key] = data
                        print("使用完整数据")
                else:
                    result[key] = data
                print(f"最终 {key} 数据: {result[key]}")
            else:
                print(f"未找到 {key} 数据")
                
        print(f"\n=== 转写结果获取完成 ===")
        print(f"最终结果: {result}")
        return result if result else None

    def delete_transcript(self, file_id: str) -> bool:
        """删除转写结果"""
        try:
            file_dir = os.path.join(self.transcripts_dir, file_id)
            if os.path.exists(file_dir):
                import shutil
                shutil.rmtree(file_dir)
            return True
        except Exception as e:
            print(f"Delete transcript error: {str(e)}")
            return False

    def get_metadata(self, file_id: str) -> dict:
        """获取转写元数据"""
        file_dir = get_transcript_dir(self.transcripts_dir, file_id)
        metadata_path = os.path.join(file_dir, "metadata.json")
        print(f"\n=== 获取元数据 ===")
        print(f"元数据路径: {metadata_path}")
        print(f"文件是否存在: {os.path.exists(metadata_path)}")
        metadata = safe_read_json(metadata_path)
        print(f"元数据内容: {metadata}")
        return metadata

# 创建全局实例
transcript_manager = TranscriptManager()
