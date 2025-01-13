import os
from datetime import datetime
from typing import Optional, List, Dict
from .config import config
from .metadata import MetadataManager
from fastapi.responses import JSONResponse
from ..utils import sanitize_filename, generate_target_filename
from ..logger import get_logger

logger = get_logger(__name__)

try:
    import wave
    def get_wav_duration(file_path: str) -> Optional[float]:
        """获取 WAV 文件时长"""
        try:
            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                return duration
        except Exception as e:
            logger.error(f"Error getting WAV duration: {e}")
            return None

    def get_audio_duration(file_path: str) -> Optional[float]:
        """获取音频文件时长"""
        try:
            # 如果是 WAV 文件，直接使用 wave 模块
            if file_path.lower().endswith('.wav'):
                return get_wav_duration(file_path)
            
            # 对于其他格式，尝试使用 FFmpeg
            import subprocess
            result = subprocess.run([
                'ffmpeg', '-i', file_path, 
                '-f', 'null', '-'
            ], capture_output=True, text=True, stderr=subprocess.PIPE)
            
            # 从 FFmpeg 输出中解析时长
            for line in result.stderr.split('\n'):
                if 'Duration:' in line:
                    time_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = time_str.split(':')
                    duration = float(h) * 3600 + float(m) * 60 + float(s)
                    return duration
            return None
        except Exception as e:
            logger.error(f"Error getting duration for {file_path}: {e}")
            return None

except ImportError:
    logger.warning("wave module not available, audio duration detection will be limited")
    def get_audio_duration(file_path: str) -> Optional[float]:
        return None

class FileOperations:
    """文件操作类"""
    def __init__(self):
        self.config = config
        self.metadata = MetadataManager()
    
    def get_audio_duration(self, file_path: str) -> Optional[float]:
        """获取音频文件时长"""
        return get_audio_duration(file_path)
    
    def save_uploaded_file(self, file_content, options):
        """保存上传的文件"""
        try:
            logger.info("=== 开始保存上传文件 ===")
            logger.debug(f"接收到的选项: {options}")
            
            # 验证必要参数
            if 'original_filename' not in options:
                error_msg = "缺少原始文件名"
                logger.error(error_msg)
                return {"code": 422, "message": error_msg}
            
            logger.debug(f"接收到的选项: {options}")
            
            # 生成文件名
            original_filename = options['original_filename']
            logger.debug(f"原始文件名: {original_filename}")
            
            target_filename, cleaned_display_name, cleaned_full_name, ext = generate_target_filename(original_filename)
            logger.info(f"生成的目标文件名: {target_filename}")
            logger.debug(f"清理后的显示名称: {cleaned_display_name}")
            logger.debug(f"文件扩展名: {ext}")
            
            # 构建文件路径
            file_path = os.path.join(self.config.audio_dir, target_filename)
            logger.info(f"目标文件路径: {file_path}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            logger.debug(f"确保目录存在: {os.path.dirname(file_path)}")
            
            # 保存文件
            logger.info(f"开始写入文件: {file_path}")
            try:
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                logger.info("文件写入成功")
            except Exception as e:
                logger.error(f"文件写入失败", exc_info=True)
                raise
            
            # 获取音频时长
            duration = self.get_audio_duration(file_path)
            logger.info(f"音频时长: {duration if duration else '未知'}秒")
            
            # 构建返回信息
            file_info = {
                'file_id': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'original_name': original_filename,
                'display_name': cleaned_display_name,
                'display_full_name': cleaned_full_name,
                'storage_name': target_filename,
                'extension': ext,
                'size': len(file_content),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'status': '已上传',
                'path': file_path,
                'duration': duration,
                'duration_str': f"{int(duration//60)}:{int(duration%60):02d}" if duration else "未知",
                'options': options
            }
            
            # 保存元数据
            logger.debug(f"准备构建元数据内容")
            metadata_content = {
                'file_id': file_info['file_id'],
                'duration': duration,
                'duration_str': file_info['duration_str'],
                'original_name': file_info['original_name'],
                'display_name': file_info['display_name'],
                'display_full_name': file_info['display_full_name'],
                'storage_name': file_info['storage_name'],
                'extension': file_info['extension'],
                'size': file_info['size'],
                'date': file_info['date'],
                'status': file_info['status'],
                'path': file_info['path'],
                'options': file_info['options']
            }
            logger.debug(f"构建的元数据内容: {metadata_content}")
            
            logger.info(f"开始更新元数据 - 文件名: {target_filename}")
            self.metadata.update(target_filename, metadata_content)
            logger.info("元数据更新完成")
            
            logger.debug(f"文件信息: {file_info}")
            
            return {
                'code': 200,
                'message': 'success',
                'data': file_info
            }
            
        except Exception as e:
            logger.error(f"保存文件失败: {str(e)}", exc_info=True)
            return {
                'code': 500,
                'message': f"保存文件失败: {str(e)}"
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
                            file_meta = self.metadata.get(filename)
                            if file_meta:
                                files.append({
                                    'file_id': file_meta['file_id'],
                                    'name': file_meta['original_name'],
                                    'display_name': file_meta['display_name'],
                                    'display_full_name': file_meta['display_full_name'],
                                    'storage_name': file_meta['storage_name'],
                                    'extension': file_meta['extension'],
                                    'size': file_meta['size'],
                                    'date': file_meta['date'],
                                    'status': file_meta['status'],
                                    'path': file_meta['path'],
                                    'duration': file_meta['duration'],
                                    'duration_str': file_meta['duration_str'],
                                    'options': file_meta['options']
                                })
                        except Exception as e:
                            logger.error(f"Error parsing filename {filename}: {str(e)}")
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
            logger.error(f"获取文件列表失败: {str(e)}")
            return {
                "code": 500,
                "message": f"获取文件列表失败: {str(e)}"
            }
    
    def _find_file(self, file_id: str) -> Optional[str]:
        """根据文件ID查找文件"""
        try:
            if not os.path.exists(self.config.audio_dir):
                logger.error(f"音频目录不存在: {self.config.audio_dir}")
                return None
            
            for filename in os.listdir(self.config.audio_dir):
                if filename.startswith(file_id):
                    logger.info(f"找到文件: {filename}")
                    return filename
                
            logger.error(f"未找到文件ID对应的文件: {file_id}")
            return None
        except Exception as e:
            logger.error(f"查找文件时发生错误: {str(e)}")
            return None

    def get_file_path(self, file_id: str) -> str:
        """获取文件路径
        Args:
            file_id: 文件ID
        Returns:
            str: 文件的绝对路径
        Raises:
            FileNotFoundError: 文件不存在时抛出
        """
        try:
            if not file_id:
                logger.error("文件ID为空")
                raise ValueError("文件ID不能为空")
            
            file_found = self._find_file(file_id)
            if not file_found:
                logger.error(f"文件不存在: {file_id}")
                raise FileNotFoundError(f"文件不存在: {file_id}")
        
            file_path = os.path.join(self.config.audio_dir, file_found)
            abs_path = os.path.abspath(file_path)
            
            if not os.path.exists(abs_path):
                logger.error(f"文件路径不存在: {abs_path}")
                raise FileNotFoundError(f"文件不存在: {abs_path}")
            
            # 获取并缓存元数据
            self.get_audio_metadata(abs_path)
            
            logger.info(f"返回文件路径: {abs_path}")
            return abs_path
            
        except Exception as e:
            logger.error(f"获取文件路径失败: {str(e)}", exc_info=True)
            raise
    
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
            logger.error(f"Rename file error: {str(e)}")
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
            logger.error(f"Update status error: {str(e)}")
            return {"code": 500, "message": f"更新状态失败: {str(e)}"}
    
    def start_recognition(self):
        try:
            # 实现识别启动逻辑
            return {
                'code': 200,
                'message': 'Recognition started',
                'data': {'status': 'success'}
            }
        except Exception as e:
            return {
                'code': 500,
                'message': f'Recognition failed: {str(e)}'
            } 

    def get_audio_metadata(self, file_path: str) -> Dict:
        """获取音频文件的元数据
        Args:
            file_path: 音频文件路径
        Returns:
            Dict: 包含音频元数据的字典
        """
        try:
            # 先检查缓存
            cache_key = f"metadata_{os.path.basename(file_path)}"
            cached = self.metadata.get(cache_key)
            if cached:
                return cached

            metadata = {
                'duration': None,
                'format': None,
                'bit_rate': None,
                'sample_rate': None,
                'channels': None
            }

            # 使用 FFmpeg 获取详细信息
            import subprocess
            result = subprocess.run([
                'ffprobe', 
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ], capture_output=True, text=True)

            if result.returncode == 0:
                import json
                probe_data = json.loads(result.stdout)
                
                # 获取格式信息
                if 'format' in probe_data:
                    format_data = probe_data['format']
                    metadata['duration'] = float(format_data.get('duration', 0))
                    metadata['format'] = format_data.get('format_name')
                    metadata['bit_rate'] = int(format_data.get('bit_rate', 0))
                
                # 获取音频流信息
                if 'streams' in probe_data:
                    for stream in probe_data['streams']:
                        if stream.get('codec_type') == 'audio':
                            metadata['sample_rate'] = int(stream.get('sample_rate', 0))
                            metadata['channels'] = int(stream.get('channels', 0))
                            break

            # 缓存结果
            self.metadata.update(cache_key, metadata)
            return metadata

        except Exception as e:
            logger.error(f"获取音频元数据失败: {str(e)}", exc_info=True)
            return {
                'duration': None,
                'format': None,
                'bit_rate': None,
                'sample_rate': None,
                'channels': None
            }

async def get_files(page: int, page_size: int, query: str):
    logger.info(f"获取文件列表 - 页码: {page}, 每页数量: {page_size}, 查询: {query}")
    # ... 其余代码 