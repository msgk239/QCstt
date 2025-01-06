# 标准库
import os
import json
import shutil
from datetime import datetime
from typing import Optional, List, Dict
from pydub import AudioSegment

class FileService:
    """文件服务类，处理文件的上传、删除、恢复等操作"""
    def __init__(self):
        # 获取项目根目录
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # 设置存储根目录
        self.storage_root = os.path.join(self.root_dir, "storage")
        self.uploads_dir = os.path.join(self.storage_root, "uploads")
        self.audio_dir = os.path.join(self.uploads_dir, "audio")
        self.trash_dir = os.path.join(self.storage_root, "trash")
        
        # 确保目录存在
        os.makedirs(self.uploads_dir, exist_ok=True)
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.trash_dir, exist_ok=True)
    
    def save_uploaded_file(self, file_content, filename, options=None):
        """保存上传的文件"""
        try:
            # 生成带时间戳的文件名（精确到秒）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{timestamp}_{filename}"
            
            # 直接保存到 audio 目录下
            file_path = os.path.join(self.audio_dir, new_filename)
            print(f"Saving file to: {file_path}")
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            print(f"File saved successfully: {file_path}")
            
            # 创建文件记录
            file_info = {
                'id': timestamp,  # 使用时间戳作为ID
                'name': filename, # 保存原始文件名
                'size': len(file_content),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': '待识别' if options and options.get('action') == 'recognize' else '已上传',
                'path': file_path,
                'options': options
            }
            
            return {
                "code": 200,
                "message": "success",
                "data": file_info
            }
            
        except Exception as e:
            return {
                "code": 500,
                "message": f"保存文件失败: {str(e)}"
            }
    
    def get_file_list(self, page=1, page_size=20, query=None):
        """获取文件列表"""
        try:
            files = []
            # 直接读取 audio 目录下的所有文件
            if os.path.exists(self.audio_dir):
                for filename in os.listdir(self.audio_dir):
                    if query and query.lower() not in filename.lower():
                        continue
                    
                    full_path = os.path.join(self.audio_dir, filename)
                    if os.path.isfile(full_path):  # 确保是文件而不是目录
                        try:
                            timestamp = filename[:15]  # YYYYMMDD_HHMMSS
                            original_name = filename[16:]  # 原始文件名
                            stat = os.stat(full_path)
                            
                            # 获取音频时长
                            duration = self.get_audio_duration(full_path)
                            duration_str = f"{int(duration//60)}:{int(duration%60):02d}" if duration else "未知"
                            
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
    
    def delete_file(self, file_id):
        """删除文件（移动到回收站）"""
        try:
            # 在 uploads/audio 目录下查找文件
            # 文件名格式：YYYYMMDD_HHMMSS_原始文件名
            # file_id 就是 YYYYMMDD_HHMMSS 部分
            file_found = None
            
            for filename in os.listdir(self.audio_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {
                    "code": 404,
                    "message": "文件不存在"
                }
            
            # 源文件完整路径
            source_path = os.path.join(self.audio_dir, file_found)
            
            # 移动到回收站
            # 在回收站中保持原始文件名
            trash_path = os.path.join(self.trash_dir, file_found)
            os.makedirs(self.trash_dir, exist_ok=True)
            
            print(f"Moving file from {source_path} to {trash_path}")  # 添加日志
            shutil.move(source_path, trash_path)
            
            return {
                "code": 200,
                "message": "success"
            }
            
        except Exception as e:
            print(f"Delete file error: {str(e)}")  # 添加错误日志
            return {
                "code": 500,
                "message": f"删除文件失败: {str(e)}"
            }
    
    def get_audio_duration(self, file_path: str) -> Optional[float]:
        """获取音频文件时长（秒）"""
        try:
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0
        except Exception as e:
            print(f"Error getting duration for {file_path}: {e}")
            return None
    
    def get_trash_list(self, page=1, page_size=20, query=None):
        """获取回收站文件列表"""
        try:
            files = []
            print(f"Checking trash directory: {self.trash_dir}")
            
            if os.path.exists(self.trash_dir):
                print(f"Trash directory exists, contents: {os.listdir(self.trash_dir)}")
                for filename in os.listdir(self.trash_dir):
                    if query and query.lower() not in filename.lower():
                        continue
                    
                    full_path = os.path.join(self.trash_dir, filename)
                    if os.path.isfile(full_path):
                        try:
                            timestamp = filename[:15]
                            original_name = filename[16:]
                            stat = os.stat(full_path)
                            
                            # 获取音频时长
                            duration = self.get_audio_duration(full_path)
                            duration_str = f"{int(duration//60)}:{int(duration%60):02d}" if duration else "未知"
                            
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
            else:
                print("Trash directory does not exist!")
            
            files.sort(key=lambda x: x['delete_date'], reverse=True)
            
            total = len(files)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            
            print(f"Found {total} files in trash")
            
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
            print(f"Get trash list error: {str(e)}")
            return {
                "code": 500,
                "message": f"获取回收站列表失败: {str(e)}"
            }
    
    def restore_file(self, file_id):
        """从回收站恢复文件"""
        try:
            # 在回收站中查找文件
            file_found = None
            for filename in os.listdir(self.trash_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {
                    "code": 404,
                    "message": "文件不存在"
                }
            
            # 源文件和目标路径
            source_path = os.path.join(self.trash_dir, file_found)
            target_path = os.path.join(self.audio_dir, file_found)
            
            # 移动文件回原目录
            print(f"Restoring file from {source_path} to {target_path}")
            shutil.move(source_path, target_path)
            
            return {
                "code": 200,
                "message": "success"
            }
            
        except Exception as e:
            print(f"Restore file error: {str(e)}")
            return {
                "code": 500,
                "message": f"恢复文件失败: {str(e)}"
            }
    
    def permanently_delete_file(self, file_id):
        """永久删除文件"""
        try:
            # 在回收站中查找文件
            file_found = None
            for filename in os.listdir(self.trash_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {
                    "code": 404,
                    "message": "文件不存在"
                }
            
            # 删除文件
            file_path = os.path.join(self.trash_dir, file_found)
            print(f"Permanently deleting file: {file_path}")
            os.remove(file_path)
            
            return {
                "code": 200,
                "message": "success"
            }
            
        except Exception as e:
            print(f"Permanently delete file error: {str(e)}")
            return {
                "code": 500,
                "message": f"永久删除文件失败: {str(e)}"
            }
    
    def clear_trash(self):
        """清空回收站"""
        try:
            # 删除回收站中的所有文件
            for filename in os.listdir(self.trash_dir):
                file_path = os.path.join(self.trash_dir, filename)
                if os.path.isfile(file_path):
                    print(f"Deleting file: {file_path}")
                    os.remove(file_path)
            
            return {
                "code": 200,
                "message": "success"
            }
            
        except Exception as e:
            print(f"Clear trash error: {str(e)}")
            return {
                "code": 500,
                "message": f"清空回收站失败: {str(e)}"
            }
    
    def get_audio_file(self, file_id):
        """获取音频文件内容"""
        try:
            # 在 audio 目录下查找文件
            file_found = None
            for filename in os.listdir(self.audio_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {
                    "code": 404,
                    "message": "文件不存在"
                }
            
            # 获取文件路径
            file_path = os.path.join(self.audio_dir, file_found)
            
            # 读取文件内容
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # 获取文件MIME类型
            file_extension = os.path.splitext(file_found)[1].lower()
            mime_types = {
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.ogg': 'audio/ogg',
                '.flac': 'audio/flac'
            }
            content_type = mime_types.get(file_extension, 'application/octet-stream')
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "content": file_content,
                    "content_type": content_type,
                    "filename": file_found[16:]  # 去掉时间戳前缀
                }
            }
            
        except Exception as e:
            print(f"Get audio file error: {str(e)}")
            return {
                "code": 500,
                "message": f"获取音频文件失败: {str(e)}"
            }
    
    def rename_file(self, file_id, new_name):
        """重命名文件"""
        try:
            # 在 audio 目录下查找文件
            file_found = None
            for filename in os.listdir(self.audio_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {
                    "code": 404,
                    "message": "文件不存在"
                }
            
            # 构建新的文件名(保持时间戳前缀不变)
            new_filename = f"{file_id}_{new_name}"
            
            # 源文件和目标文件路径
            old_path = os.path.join(self.audio_dir, file_found)
            new_path = os.path.join(self.audio_dir, new_filename)
            
            # 检查新文件名是否已存在
            if os.path.exists(new_path):
                return {
                    "code": 400,
                    "message": "文件名已存在"
                }
            
            # 重命名文件
            os.rename(old_path, new_path)
            
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
            return {
                "code": 500,
                "message": f"重命名文件失败: {str(e)}"
            }

# 创建全局实例
file_service = FileService()