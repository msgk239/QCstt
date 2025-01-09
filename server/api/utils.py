import os

def get_file_path(base_dir, file_id):
    """获取文件的完整路径"""
    return os.path.join(base_dir, file_id)

def update_file_status(file_service, file_id, status):
    """更新文件状态"""
    file_service.update_file_status(file_id, status) 