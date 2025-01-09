from .config import config
from .metadata import MetadataManager
from .operations import FileOperations
from .trash import TrashManager

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

# 创建全局实例
file_service = FileService()