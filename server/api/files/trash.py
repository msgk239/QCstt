import os
import shutil
from datetime import datetime
from typing import Optional, Dict
from .config import config
from .metadata import MetadataManager

class TrashManager:
    """回收站管理类"""
    def __init__(self):
        self.config = config
        self.metadata = MetadataManager()
    
    def _find_file(self, file_id: str) -> Optional[str]:
        """在音频目录中查找文件"""
        if os.path.exists(self.config.audio_dir):
            for filename in os.listdir(self.config.audio_dir):
                if filename.startswith(file_id):
                    return filename
        return None
    
    def _find_file_in_trash(self, file_id: str) -> Optional[str]:
        """在回收站中查找文件"""
        if os.path.exists(self.config.trash_dir):
            for filename in os.listdir(self.config.trash_dir):
                if filename.startswith(file_id):
                    return filename
        return None
    
    def get_trash_list(self, page=1, page_size=20, query=None) -> Dict:
        """获取回收站文件列表"""
        try:
            files = []
            if os.path.exists(self.config.trash_dir):
                for filename in os.listdir(self.config.trash_dir):
                    if query and query.lower() not in filename.lower():
                        continue
                    
                    full_path = os.path.join(self.config.trash_dir, filename)
                    if os.path.isfile(full_path):
                        try:
                            timestamp = filename[:15]
                            original_name = filename[16:]
                            stat = os.stat(full_path)
                            
                            # 获取音频时长
                            file_meta = self.metadata.get(filename)
                            duration_str = file_meta.get('duration_str', '未知')
                            
                            files.append({
                                'id': timestamp,
                                'name': original_name,
                                'size': stat.st_size,
                                'date': datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
                                'delete_date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                                'path': full_path,
                                'duration': duration_str
                            })
                        except Exception as e:
                            print(f"Error parsing filename {filename}: {str(e)}")
                            continue
            
            files.sort(key=lambda x: x['delete_date'], reverse=True)
            
            total = len(files)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "items": files[start_idx:end_idx],
                    "total": total,
                    "page": page,
                    "page_size": page_size
                }
            }
            
        except Exception as e:
            return {"code": 500, "message": f"获取回收站列表失败: {str(e)}"}
    
    def permanently_delete_file(self, file_id: str) -> Dict:
        """永久删除文件"""
        try:
            file_found = self._find_file_in_trash(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            file_path = os.path.join(self.config.trash_dir, file_found)
            os.remove(file_path)
            
            # 从元数据中删除
            self.metadata.delete(file_found)
            
            return {"code": 200, "message": "success"}
        except Exception as e:
            return {"code": 500, "message": f"永久删除文件失败: {str(e)}"}
    
    def clear_trash(self) -> Dict:
        """清空回收站"""
        try:
            deleted_count = 0
            for filename in os.listdir(self.config.trash_dir):
                file_path = os.path.join(self.config.trash_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    self.metadata.delete(filename)
                    deleted_count += 1
            
            return {
                "code": 200,
                "message": "success",
                "data": {"deleted_count": deleted_count}
            }
        except Exception as e:
            return {"code": 500, "message": f"清空回收站失败: {str(e)}"}
    
    def move_to_trash(self, file_id):
        """移动文件到回收站"""
        try:
            file_found = self._find_file(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            source_path = os.path.join(self.config.audio_dir, file_found)
            trash_path = os.path.join(self.config.trash_dir, file_found)
            shutil.move(source_path, trash_path)
            self.metadata.delete(file_found)
            
            return {"code": 200, "message": "success"}
        except Exception as e:
            return {"code": 500, "message": f"移动到回收站失败: {str(e)}"}
    
    def restore_file(self, file_id):
        """从回收站恢复文件"""
        try:
            file_found = self._find_file_in_trash(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            source_path = os.path.join(self.config.trash_dir, file_found)
            target_path = os.path.join(self.config.audio_dir, file_found)
            shutil.move(source_path, target_path)
            
            return {"code": 200, "message": "success"}
        except Exception as e:
            return {"code": 500, "message": f"恢复文件失败: {str(e)}"} 