# 标准库导入
from typing import Dict, List, Optional
from ..logger import get_logger
import os
from datetime import datetime
from email.utils import formatdate
from fastapi.responses import FileResponse, JSONResponse
from fastapi import HTTPException
from pydub import AudioSegment
import time

# 内部模块导入
from .config import config
from .metadata import MetadataManager
from .operations import FileOperations
from .trash import TrashManager
from .storage import File, FileStorage
from .exceptions import FileNotFoundError, FileServiceError

# 相关服务导入
from ..speech.storage import transcript_manager
from ..speech.recognize import speech_service
from ..utils import generate_target_filename, get_audio_metadata, safe_write_json, ensure_dir

logger = get_logger(__name__)

class FileService:
    """文件服务主类"""
    def __init__(self, storage_dir: str):
        self.config = config
        self.metadata = MetadataManager()
        self.operations = FileOperations()
        self.trash = TrashManager()
        self.uploads_dir = config.uploads_dir
        self.storage_dir = config.storage_root  # 使用storage_root而不是uploads_dir
        self.storage = FileStorage(storage_dir)
        ensure_dir(storage_dir)
    
    def save_uploaded_file(self, file_content, filename, options=None):
        """保存上传的文件，生成标准文件ID"""
        try:
            logger.info(f"开始处理文件上传")
            
            # 验证参数
            if not file_content:
                error_msg = "文件内容为空"
                logger.error(error_msg)
                return {"code": 422, "message": error_msg}
            
            # 准备选项
            upload_options = options or {}
            upload_options['original_filename'] = filename
            upload_options['language'] = upload_options.get('language', 'zh')
            
            # 调用 operations 处理文件保存
            return self.operations.save_uploaded_file(file_content, upload_options)
            
        except Exception as e:
            logger.error(f"处理文件上传失败: {str(e)}", exc_info=True)
            return {
                'code': 500,
                'message': f'保存文件失败: {str(e)}'
            }
    
    def get_file_list(self, page: int, page_size: int, query: str = None):
        logger.info(f"获取文件列表 - 页码: {page}, 每页数量: {page_size}, 查询: {query}")
        return self.operations.get_file_list(page, page_size, query)
    
    def get_file_path(self, file_id):
        """获取文件路径
        Args:
            file_id: 文件ID
        Returns:
            Dict: 包含文件路径的响应
        """
        try:
            file_path = self.operations.get_file_path(file_id)
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "path": file_path,
                    "filename": os.path.basename(file_path)
                }
            }
        except FileNotFoundError as e:
            logger.error(str(e))
            return {
                "code": 404,
                "message": "文件不存在"
            }
        except ValueError as e:
            logger.error(str(e))
            return {
                "code": 400,
                "message": str(e)
            }
        except Exception as e:
            logger.error(f"获取文件路径失败: {str(e)}", exc_info=True)
            return {
                "code": 500,
                "message": f"获取文件路径失败: {str(e)}"
            }
    
    def delete_file(self, file_id: str):
        logger.info(f"删除文件: {file_id}")
        # 同时删除转写结果
        transcript_manager.delete_transcript(file_id)
        return self.trash.move_to_trash(file_id)
    
    def restore_file(self, file_id):
        return self.trash.restore_file(file_id)
    
    def get_trash_list(self, page=1, page_size=20, query=None):
        return self.trash.get_trash_list(page, page_size, query)
    
    def permanently_delete_file(self, file_id):
        # 同时删除转写结果
        transcript_manager.delete_transcript(file_id)
        return self.trash.permanently_delete_file(file_id)
    
    def clear_trash(self):
        return self.trash.clear_trash()
    
    def rename_file(self, file_id, new_name):
        """重命名文件
        Args:
            file_id: 原文件ID 
            new_name: 新文件名 (timestamp_new_name.wav)
        """
        try:
            # 验证新文件名格式是否正确
            if not new_name.startswith(file_id.split('_')[0]):
                # 如果新文件名没有保持原有时间戳，返回错误
                return {
                    "code": 400,
                    "message": "新文件名格式不正确"
                }
            
            return self.operations.rename_file(file_id, new_name)
            
        except Exception as e:
            print(f"Rename file error: {str(e)}")
            return {
                "code": 500,
                "message": f"重命名文件失败: {str(e)}"
            }
    
    def update_file_status(self, file_id, status):
        return self.operations.update_file_status(file_id, status)
    
    def get_file_detail(self, file_id: str) -> dict:
        """获取文件详情，包括识别结果"""
        logger.info(f"获取文件详情: {file_id}")
        try:
            file_info = self.get_file_path(file_id)
            
            if file_info["code"] != 200:
                return file_info
                
            file_path = file_info["data"]["path"]
            logger.debug(f"文件路径: {file_path}")
            
            # 获取转写结果

            transcripts = transcript_manager.get_transcript(file_id)
            
            # 获取两种元数据
            # 1. 从 转写metadata 获取的元数据
            transcript_metadata = transcript_manager.get_metadata(file_id)
            
            # 2. 从 文件metadata 获取的元数据
            metadata_result = self.metadata.get_by_file_id(file_id)
            
            # 合并元数据：优先使用 transcript_metadata 的值
            metadata = {**metadata_result, **transcript_metadata}
            
            # 构建响应
            status = metadata.get("status", "未识别") if metadata else "未识别"
            recognition_result = None
            
            # 检查转写结果
            if transcripts and "original" in transcripts:
                recognition_result = transcripts["original"]
                # 如果original中包含data字段，则取data
                if isinstance(recognition_result, dict) and "data" in recognition_result:
                    recognition_result = recognition_result["data"]
                
            # 从元数据中获取原始文件名
            original_filename = metadata.get("original_filename") if metadata else file_id
            
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    **recognition_result,
                    **metadata
                }
            }
            logger.debug(f"\n最终响应: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Get file detail error: {str(e)}", exc_info=True)
            return {
                "code": 500,
                "message": f"获取文件详情失败: {str(e)}"
            }
    
    def save_recognition_result(self, file_id: str, result: dict) -> dict:
        """保存识别结果"""
        success = transcript_manager.save_result(file_id, result)
        if success:
            # 更新文件状态
            self.update_file_status(file_id, "已完成")
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "file_id": file_id,
                    "status": "已完成"
                }
            }
        return {
            "code": 500,
            "message": "保存识别结果失败"
        }
    
    def get_recognition_result(self, file_id: str) -> dict:
        """获取识别结果"""
        transcripts = transcript_manager.get_transcript(file_id)
        if transcripts and "original" in transcripts:
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "file_id": file_id,
                    **transcripts["original"]
                }
            }
        return {
            "code": 404,
            "message": "识别结果不存在"
        }
    
    def process_audio(self, audio_file: bytes, language: str = "auto") -> Dict:
        """处理音频文件，进行语音识别"""
        try:
            # 调用语音识别服务
            result = speech_service.process_audio(audio_file, language)
            
            if result.get("code") == 200:
                # 保存识别结果
                file_id = result.get("data", {}).get("file_id")
                if file_id:
                    save_result = self.save_recognition_result(file_id, result)
                    return save_result
                else:
                    return {
                        "code": 400,
                        "message": "识别结果中缺少file_id"
                    }
            
            return result
            
        except Exception as e:
            return {
                "code": 500,
                "message": f"处理音频失败: {str(e)}"
            }
    
    def get_supported_languages(self) -> Dict:
        """获取支持的语言列表"""
        return speech_service.get_languages()
    
    def get_file_info(self, file_id):
        try:
            # 先从数据库获取文件对象
            file = self.db.query(File).filter(File.id == file_id).first()
            if not file:
                raise FileNotFoundError(f"文件不存在: {file_id}")
            
            return {
                "filename": file.name,  # 返回原始文件名
                "speech_type": file.speech_type,  # 单独返回语音类型
                # ...
            }
        except Exception as e:
            raise FileServiceError(f"获取文件信息失败: {str(e)}")
    
    def start_recognition(self, file_id: str) -> Dict:
        """开始语音识别"""
        try:
            # 获取文件路径
            file_info = self.get_file_path(file_id)
            if file_info["code"] != 200:
                return file_info
                
            file_path = file_info["data"]["path"]
            
            # 直接从 metadata 获取语言设置，默认为中文
            metadata = self.metadata.get_by_file_id(file_id) or {}
            language = metadata.get("options", {}).get("language", "zh")
            
            # 读取音频文件
            with open(file_path, "rb") as f:
                audio_content = f.read()
            
            # 调用语音识别服务
            result = speech_service.process_audio(audio_content, language)
            
            # 如果识别成功，更新文件状态和保存结果
            if result["code"] == 200:
                self.update_file_status(file_id, "已完成")
                transcript_manager.save_result(file_id, result)
            
            return result
            
        except Exception as e:
            return {
                "code": 500,
                "message": f"识别失败: {str(e)}"
            }
    
    def get_recognition_progress(self, file_id: str) -> Dict:
        """获取识别进度
        Args:
            file_id: 文件ID
        Returns:
            Dict: 包含进度信息的字典
        """
        try:
            # 获取文件详情
            file_info = self.get_file_detail(file_id)
            if file_info["code"] != 200:
                return {
                    "code": file_info["code"],
                    "message": file_info["message"],
                    "data": {
                        "progress": 0,
                        "status": "error",
                        "message": file_info["message"]
                    }
                }
            
            # 获取文件状态
            status = file_info["data"]["status"]
            
            # 根据状态返回进度信息
            if status == "已完成":
                return {
                    "code": 200,
                    "message": "success",
                    "data": {
                        "progress": 100,
                        "status": status,
                        "message": "识别完成"
                    }
                }
            elif status == "识别中":
                # 这里可以根据实际情况计算进度
                # 目前简单返回 50% 进度
                return {
                    "code": 200,
                    "message": "success",
                    "data": {
                        "progress": 50,
                        "status": status,
                        "message": "正在识别..."
                    }
                }
            else:
                return {
                    "code": 200,
                    "message": "success",
                    "data": {
                        "progress": 0,
                        "status": status,
                        "message": "未开始识别"
                    }
                }
                
        except Exception as e:
            logger.error(f"Get recognition progress error: {str(e)}")
            return {
                "code": 500,
                "message": f"获取识别进度失败: {str(e)}",
                "data": {
                    "progress": 0,
                    "status": "error",
                    "message": str(e)
                }
            }
    
    def get_audio_file(self, file_id: str):
        """获取音频文件"""
        logger.error(f"=== 开始获取音频文件 === file_id: {file_id}")
        try:
            # 获取文件路径
            file_info = self.get_file_path(file_id)
            logger.info(f"获取文件路径结果: {file_info}")
            
            if file_info["code"] != 200:
                logger.error(f"文件不存在: {file_id}")
                raise FileNotFoundError(f"文件不存在: {file_id}")
            
            file_path = file_info["data"]["path"]
            logger.info(f"文件路径: {file_path}")
            
            # 检查文件是否存在和可读
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"文件不存在: {file_path}")
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"文件不可读: {file_path}")
            
            # 获取文件扩展名和MIME类型
            extension = os.path.splitext(file_path)[1].lower()
            logger.info(f"文件扩展名: {extension}")
            
            mime_types = {
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.ogg': 'audio/ogg',
                '.m4a': 'audio/mp4',
                '.aac': 'audio/aac'
            }
            
            if extension not in mime_types:
                logger.info(f"不支持的格式，转换为 mp3: {extension}")
                # 如果是不支持的格式，使用 pydub 转换为 mp3
                audio = AudioSegment.from_file(file_path)
                temp_path = file_path.rsplit('.', 1)[0] + '.mp3'
                audio.export(temp_path, format='mp3')
                file_path = temp_path
                media_type = 'audio/mpeg'
                logger.info(f"转换后的文件路径: {file_path}")
            else:
                media_type = mime_types[extension]
                logger.info(f"媒体类型: {media_type}")
            
            # 设置响应头
            headers = {
                'Accept-Ranges': 'bytes',
                'Content-Disposition': f'inline; filename="{os.path.basename(file_path)}"',
                'Cache-Control': 'public, max-age=31536000',
                'ETag': f'"{os.path.getmtime(file_path)}"',
                'Last-Modified': formatdate(os.path.getmtime(file_path), usegmt=True)
            }
            logger.info(f"响应头: {headers}")
            
            response = FileResponse(
                path=file_path,
                media_type=media_type,
                filename=os.path.basename(file_path),
                headers=headers
            )
            logger.info(f"响应对象类型: {type(response)}")
            logger.info(f"响应对象属性: {dir(response)}")
            return response
            
        except Exception as e:
            logger.error(f"获取音频文件失败: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=404 if isinstance(e, FileNotFoundError) else 500,
                detail=str(e)
            )

    def save_version(self, file_id: str, data: dict) -> dict:
        """保存新版本
        Args:
            file_id: 文件ID
            data: 版本内容
        """
        try:
            logger.info(f"保存版本 - file_id: {file_id}")
            
            # 检查参数
            if not file_id or not isinstance(file_id, str):
                return {"code": 400, "message": f"无效的文件ID: {file_id}"}
            
            if not data or not isinstance(data, dict):
                return {"code": 400, "message": "无效的数据内容"}
            
            # 构建版本目录
            version_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            version_dir = os.path.join(self.config.versions_dir, file_id, version_timestamp)
            
            # 确保目录存在
            if not ensure_dir(version_dir):
                return {"code": 500, "message": "创建版本目录失败"}
            
            # 保存内容和元数据
            content_path = os.path.join(version_dir, 'content.json')
            metadata_path = os.path.join(version_dir, 'metadata.json')
            
            # 构建元数据
            metadata = {
                'version': version_timestamp,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': data.get('type', 'manual'),
                'note': data.get('note', '')
            }
            
            if 'content' in data:
                content = data['content']
                metadata.update({
                    'segments_count': len(content.get('segments', [])),
                    'speakers_count': len(content.get('speakers', []))
                })
            
            # 保存文件
            if not safe_write_json(content_path, data):
                return {"code": 500, "message": "保存内容失败"}
                
            if not safe_write_json(metadata_path, metadata):
                return {"code": 500, "message": "保存元数据失败"}
            
            logger.info(f"版本保存成功 - {version_timestamp}")
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "file_id": file_id,
                    "version": version_timestamp,
                    "path": content_path,
                    "metadata": metadata
                }
            }
                
        except Exception as e:
            logger.error(f"保存版本失败: {str(e)}", exc_info=True)
            return {
                "code": 500,
                "message": f"保存版本失败: {str(e)}"
            }

    def get_versions(self, file_id: str) -> dict:
        """获取版本列表"""
        try:
            # 验证文件是否存在
            file_found = self.operations._find_file(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 获取元数据
            file_meta = self.metadata.get(file_found)
            versions = file_meta.get("versions", [])
            
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "versions": versions
                }
            }
            
        except Exception as e:
            logger.error(f"获取版本列表失败: {str(e)}", exc_info=True)
            return {"code": 500, "message": f"获取版本列表失败: {str(e)}"}

    def get_version(self, file_id: str, version_id: str) -> dict:
        """获取指定版本内容"""
        try:
            # 验证文件是否存在
            file_found = self.operations._find_file(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 获取元数据
            file_meta = self.metadata.get(file_found)
            versions = file_meta.get("versions", [])
            
            # 查找指定版本
            version = next((v for v in versions if v["id"] == version_id), None)
            if not version:
                return {"code": 404, "message": "版本不存在"}
            
            return {
                "code": 200,
                "message": "success",
                "data": version
            }
            
        except Exception as e:
            logger.error(f"获取版本内容失败: {str(e)}", exc_info=True)
            return {"code": 500, "message": f"获取版本内容失败: {str(e)}"}

    def restore_version(self, file_id: str, version_id: str) -> dict:
        """还原到指定版本"""
        try:
            # 验证文件是否存在
            file_found = self.operations._find_file(file_id)
            if not file_found:
                return {"code": 404, "message": "文件不存在"}
            
            # 获取元数据
            file_meta = self.metadata.get(file_found)
            versions = file_meta.get("versions", [])
            
            # 查找指定版本
            version = next((v for v in versions if v["id"] == version_id), None)
            if not version:
                return {"code": 404, "message": "版本不存在"}
            
            # 创建新版本（记录还原操作）
            restore_version = {
                "id": f"{int(time.time())}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "content": version["content"],
                "type": "restore",
                "note": f"还原自版本 {version_id}",
                "restored_from": version_id
            }
            
            # 添加新版本到列表开头
            versions.insert(0, restore_version)
            
            # 限制版本数量
            MAX_VERSIONS = 50
            if len(versions) > MAX_VERSIONS:
                versions = versions[:MAX_VERSIONS]
            
            # 更新元数据
            file_meta["versions"] = versions
            self.metadata.update(file_found, file_meta)
            
            return {
                "code": 200,
                "message": "success",
                "data": restore_version
            }
            
        except Exception as e:
            logger.error(f"还原版本失败: {str(e)}", exc_info=True)
            return {"code": 500, "message": f"还原版本失败: {str(e)}"}

    def save_file(self, file_id: str, data: Dict) -> Dict:
        """保存文件内容
        Args:
            file_id: 文件ID
            data: 文件数据，包含 segments 和 speakers
        Returns:
            Dict: 包含保存结果的响应
        """
        try:
            logger.info(f"开始保存文件版本 - file_id: {file_id}")
            logger.debug(f"保存的数据内容: {data}")
            
            # 使用config中的versions_dir
            version_dir = os.path.join(self.config.versions_dir, file_id)
            logger.info(f"版本目录路径: {version_dir}")
            ensure_dir(version_dir)
            
            # 生成版本时间戳
            version_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            current_version_dir = os.path.join(version_dir, version_timestamp)
            logger.info(f"当前版本目录: {current_version_dir}")
            ensure_dir(current_version_dir)
            
            # 构建文件路径
            file_path = os.path.join(current_version_dir, 'content.json')
            logger.info(f"文件保存路径: {file_path}")
            
            # 保存文件内容
            if safe_write_json(file_path, data):
                logger.info("文件内容保存成功")
                # 更新元数据
                metadata_path = os.path.join(current_version_dir, 'metadata.json')
                metadata = {
                    'version': version_timestamp,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'segments_count': len(data.get('segments', [])),
                    'speakers_count': len(data.get('speakers', [])),
                    'status': 'saved'
                }
                safe_write_json(metadata_path, metadata)
                logger.info("元数据保存成功")
                
                response = {
                    "code": 200,
                    "message": "版本保存成功",
                    "data": {
                        "file_id": file_id,
                        "version": version_timestamp,
                        "path": file_path,
                        "metadata": metadata
                    }
                }
                logger.info(f"保存完成，返回响应: {response}")
                return response
            else:
                logger.error("文件内容保存失败")
                raise FileServiceError("保存版本失败")
                
        except Exception as e:
            logger.error(f"保存版本失败: {str(e)}", exc_info=True)
            return {
                "code": 500,
                "message": f"保存版本失败: {str(e)}"
            }

# 创建全局实例
file_service = FileService(config.uploads_dir)