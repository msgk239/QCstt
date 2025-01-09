# 标准库
import os
import json
import shutil
from datetime import datetime
from typing import Optional, List, Dict
from pydub import AudioSegment
import time

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
        
        self.metadata_file = os.path.join(self.storage_root, "metadata.json")
        self._load_metadata()
    
    def _load_metadata(self):
        """加载元数据"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {}
        except Exception as e:
            print(f"加载元数据失败: {e}")
            self.metadata = {}
    
    def _save_metadata(self):
        """保存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存元数据失败: {e}")
    
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
            
            # 获取音频时长并保存到元数据
            duration = self.get_audio_duration(file_path)
            self.metadata[new_filename] = {
                'duration': duration,
                'duration_str': f"{int(duration//60)}:{int(duration%60):02d}" if duration else "未知"
            }
            self._save_metadata()
            
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
            if os.path.exists(self.audio_dir):
                for filename in os.listdir(self.audio_dir):
                    if query and query.lower() not in filename.lower():
                        continue
                    
                    full_path = os.path.join(self.audio_dir, filename)
                    if os.path.isfile(full_path):
                        try:
                            timestamp = filename[:15]
                            original_name = filename[16:]
                            stat = os.stat(full_path)
                            
                            # 从元数据中获取时长
                            file_meta = self.metadata.get(filename, {})
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
    
    def delete_file(self, file_id):
        """删除文件（移动到回收站）"""
        try:
            file_found = None
            for filename in os.listdir(self.audio_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 移动到回收站
            source_path = os.path.join(self.audio_dir, file_found)
            trash_path = os.path.join(self.trash_dir, file_found)
            shutil.move(source_path, trash_path)
            
            # 更新元数据
            if file_found in self.metadata:
                del self.metadata[file_found]
                self._save_metadata()
            
            return {"code": 200, "message": "success"}
            
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
            file_found = None
            for filename in os.listdir(self.trash_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 恢复文件
            source_path = os.path.join(self.trash_dir, file_found)
            target_path = os.path.join(self.audio_dir, file_found)
            shutil.move(source_path, target_path)
            
            # 重新计算时长并更新元数据
            duration = self.get_audio_duration(target_path)
            self.metadata[file_found] = {
                'duration': duration,
                'duration_str': f"{int(duration//60)}:{int(duration%60):02d}" if duration else "未知"
            }
            self._save_metadata()
            
            return {"code": 200, "message": "success"}
            
        except Exception as e:
            print(f"Restore file error: {str(e)}")
            return {
                "code": 500,
                "message": f"恢复文件失败: {str(e)}"
            }
    
    def permanently_delete_file(self, file_id):
        """永久删除文件"""
        try:
            file_found = None
            for filename in os.listdir(self.trash_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 删除文件
            file_path = os.path.join(self.trash_dir, file_found)
            os.remove(file_path)
            
            # 从元数据中删除
            if file_found in self.metadata:
                del self.metadata[file_found]
                self._save_metadata()
            
            return {"code": 200, "message": "success"}
            
        except Exception as e:
            print(f"Permanently delete file error: {str(e)}")
            return {"code": 500, "message": f"永久删除文件失败: {str(e)}"}
    
    def clear_trash(self):
        """清空回收站"""
        try:
            deleted_count = 0
            for filename in os.listdir(self.trash_dir):
                file_path = os.path.join(self.trash_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    # 从元数据中删除
                    if filename in self.metadata:
                        del self.metadata[filename]
                    deleted_count += 1
            
            # 保存元数据
            if deleted_count > 0:
                self._save_metadata()
            
            return {
                "code": 200, 
                "message": "success",
                "data": {"deleted_count": deleted_count}
            }
            
        except Exception as e:
            print(f"Clear trash error: {str(e)}")
            return {"code": 500, "message": f"清空回收站失败: {str(e)}"}
    
    def rename_file(self, file_id, new_name):
        """重命名文件"""
        try:
            file_found = None
            for filename in os.listdir(self.audio_dir):
                if filename.startswith(file_id):
                    file_found = filename
                    break
            
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 构建新的文件名(保持时间戳前缀不变)
            new_filename = f"{file_id}_{new_name}"
            
            # 源文件和目标文件路径
            old_path = os.path.join(self.audio_dir, file_found)
            new_path = os.path.join(self.audio_dir, new_filename)
            
            # 检查新文件名是否已存在
            if os.path.exists(new_path):
                return {"code": 400, "message": "文件名已存在"}
            
            # 重命名文件
            os.rename(old_path, new_path)
            
            # 更新元数据
            if file_found in self.metadata:
                self.metadata[new_filename] = self.metadata[file_found]
                del self.metadata[file_found]
                self._save_metadata()
            
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
    
    def get_file_path(self, file_id):
        """获取文件的实际路径"""
        try:
            # 查找文件
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
            
            file_path = os.path.join(self.audio_dir, file_found)
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "path": os.path.abspath(file_path),
                    "filename": file_found[16:]  # 去掉时间戳前缀
                }
            }
        except Exception as e:
            print(f"Get file path error: {str(e)}")
            return {
                "code": 500,
                "message": f"获取文件路径失败: {str(e)}"
            }

# 创建全局实例
file_service = FileService()