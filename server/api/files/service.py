from .config import config
from .metadata import MetadataManager
from .operations import FileOperations
from .trash import TrashManager
import json
import os

class FileService:
    """文件服务主类"""
    def __init__(self):
        self.config = config
        self.metadata = MetadataManager()
        self.operations = FileOperations()
        self.trash = TrashManager()
    
    def save_uploaded_file(self, file_content, filename, options=None):
        return self.operations.save_uploaded_file(file_content, filename, options)
    
    def get_file_list(self, page=1, page_size=20, query=None):
        return self.operations.get_file_list(page, page_size, query)
    
    def get_file_path(self, file_id):
        return self.operations.get_file_path(file_id)
    
    def delete_file(self, file_id):
        return self.trash.move_to_trash(file_id)
    
    def restore_file(self, file_id):
        return self.trash.restore_file(file_id)
    
    def get_trash_list(self, page=1, page_size=20, query=None):
        return self.trash.get_trash_list(page, page_size, query)
    
    def permanently_delete_file(self, file_id):
        return self.trash.permanently_delete_file(file_id)
    
    def clear_trash(self):
        return self.trash.clear_trash()
    
    def rename_file(self, file_id, new_name):
        return self.operations.rename_file(file_id, new_name)
    
    def update_file_status(self, file_id, status):
        return self.operations.update_file_status(file_id, status)
    
    def get_file_detail(self, file_id: str) -> dict:
        """获取文件详情，包括识别结果
        
        Args:
            file_id: 文件ID
            
        Returns:
            包含文件信息和识别结果的字典
        """
        try:
            # 获取文件基本信息
            file_info = self.get_file_path(file_id)
            if file_info["code"] != 200:
                return file_info
                
            file_path = file_info["data"]["path"]
            
            # 读取识别结果文件（如果存在）
            result_path = file_path + ".json"
            if os.path.exists(result_path):
                with open(result_path, "r", encoding="utf-8") as f:
                    recognition_result = json.load(f)
            else:
                recognition_result = None
                
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "id": file_id,
                    "name": file_info["data"]["filename"],
                    "path": file_path,
                    "status": "已完成" if recognition_result else "未识别",
                    "recognition_result": recognition_result
                }
            }
            
        except Exception as e:
            print(f"Get file detail error: {str(e)}")
            return {
                "code": 500,
                "message": f"获取文件详情失败: {str(e)}"
            }

# 创建全局实例
file_service = FileService()