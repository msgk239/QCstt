import os
from datetime import datetime
try:
    from pydub import AudioSegment
except ImportError:
    print("Warning: pydub not installed. Audio duration detection will be disabled.")
    AudioSegment = None

from typing import Optional, List, Dict
from .config import config
from .metadata import MetadataManager

class FileOperations:
    """文件操作类"""
    def __init__(self):
        self.config = config
        self.metadata = MetadataManager()
    
    def get_audio_duration(self, file_path: str) -> Optional[float]:
        """获取音频文件时长"""
        try:
            if AudioSegment is None:
                print("Warning: pydub not available")
                return None
                
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except Exception as e:
            print(f"Error getting duration for {file_path}: {e}")
            return None
    
    def save_uploaded_file(self, file_content, file_id, options=None):
        """保存上传的文件"""
        try:
            # 使用配置的音频目录
            file_path = os.path.join(self.config.audio_dir, file_id)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # 获取音频时长
            duration = self.get_audio_duration(file_path)
            
            # 获取文件信息
            file_info = {
                'id': file_id.rsplit('.', 1)[0],  # 去掉扩展名
                'name': file_id,
                'size': len(file_content),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': '已上传',
                'path': file_path,
                'duration': duration,
                'duration_str': f"{int(duration//60)}:{int(duration%60):02d}" if duration else "未知",
                'options': options
            }
            
            # 保存元数据
            self.metadata.update(file_id, {
                'duration': duration,
                'duration_str': file_info['duration_str']
            })
            
            return {
                'code': 200,
                'message': 'success',
                'data': file_info
            }
            
        except Exception as e:
            print(f"Save file error: {str(e)}")
            return {
                'code': 500,
                'message': f'保存文件失败: {str(e)}'
            }
    
    def get_file_list(self, page=1, page_size=20, query=None) -> Dict:
        """获取文件列表"""
        try:
            files = []
            if os.path.exists(self.config.audio_dir):
                for filename in os.listdir(self.config.audio_dir):
                    if query and query.lower() not in filename.lower():
                        continue
                    
                    full_path = os.path.join(self.config.audio_dir, filename)
                    if os.path.isfile(full_path):
                        try:
                            timestamp = filename[:15]
                            original_name = filename[16:]
                            stat = os.stat(full_path)
                            
                            # 从元数据中获取时长
                            file_meta = self.metadata.get(filename)
                            duration_str = file_meta.get('duration_str', '未知')
                            
                            files.append({
                                'id': timestamp,
                                'name': original_name,
                                'size': stat.st_size,
                                'date': datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S'),
                                'status': '已上传',
                                'path': full_path,
                                'duration': duration_str
                            })
                        except Exception as e:
                            print(f"Error parsing filename {filename}: {str(e)}")
                            continue
            
            # 按日期倒序排序
            files.sort(key=lambda x: x['date'], reverse=True)
            
            # 分页
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
            print(f"Get file list error: {str(e)}")
            return {
                "code": 500,
                "message": f"获取文件列表失败: {str(e)}"
            }
    
    def get_file_path(self, file_id: str) -> Dict:
        """获取文件的实际路径"""
        try:
            file_found = self._find_file(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            file_path = os.path.join(self.config.audio_dir, file_found)
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "path": os.path.abspath(file_path),
                    "filename": file_found[16:]  # 去掉时间戳前缀
                }
            }
        except Exception as e:
            return {"code": 500, "message": f"获取文件路径失败: {str(e)}"}
    
    def _find_file(self, file_id: str) -> Optional[str]:
        """根据文件ID查找文件"""
        if os.path.exists(self.config.audio_dir):
            for filename in os.listdir(self.config.audio_dir):
                if filename.startswith(file_id):
                    return filename
        return None 
    
    def rename_file(self, file_id: str, new_name: str) -> Dict:
        """重命名文件"""
        try:
            file_found = self._find_file(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 构建新的文件名(保持时间戳前缀不变)
            new_filename = f"{file_id}_{new_name}"
            
            # 源文件和目标文件路径
            old_path = os.path.join(self.config.audio_dir, file_found)
            new_path = os.path.join(self.config.audio_dir, new_filename)
            
            # 检查新文件名是否已存在
            if os.path.exists(new_path):
                return {"code": 400, "message": "文件名已存在"}
            
            # 重命名文件
            os.rename(old_path, new_path)
            
            # 更新元数据
            if file_found in self.metadata.metadata:
                self.metadata.update(new_filename, self.metadata.get(file_found))
                self.metadata.delete(file_found)
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "id": file_id,
                    "name": new_name
                }
            }
            
        except Exception as e:
            print(f"Rename file error: {str(e)}")
            return {"code": 500, "message": f"重命名文件失败: {str(e)}"}
    
    def update_file_status(self, file_id: str, status: str) -> Dict:
        """更新文件状态"""
        try:
            file_found = self._find_file(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 更新元数据中的状态
            file_meta = self.metadata.get(file_found)
            file_meta["status"] = status
            self.metadata.update(file_found, file_meta)
            
            return {
                "code": 200,
                "message": "success",
                "data": {"status": status}
            }
            
        except Exception as e:
            print(f"Update status error: {str(e)}")
            return {"code": 500, "message": f"更新状态失败: {str(e)}"} 