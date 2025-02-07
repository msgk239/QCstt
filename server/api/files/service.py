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
import json

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
        self.storage_dir = config.storage_root
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
                    **(recognition_result or {}),  # 先放recognition_result
                    **metadata,  # 再放metadata，这样可以覆盖recognition_result中的重复字段
                    "status": status,  # 确保状态字段存在
                    "original_filename": original_filename  # 确保原始文件名字段存在
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

    def save_content(self, file_id: str, data: dict) -> dict:
        """保存文件内容，同时保持原有转写结果
        Args:
            file_id: 文件ID
            data: 文件数据，包含 segments 和 speakers
        Returns:
            Dict: 包含保存结果的响应
        """
        try:
            logger.info(f"开始保存文件内容 - file_id: {file_id}")
            logger.info(f"data类型: {type(data)}")
            logger.info(f"segments类型: {type(data.get('segments'))}")  # 看看 segments 的类型
            logger.info(f"segments内容: {data.get('segments')}")  # 看看具体内容
            
            # 1. 获取转写文件路径
            transcript_dir = os.path.join(self.config.transcripts_dir, file_id)
            original_path = os.path.join(transcript_dir, 'original.json')
            backup_path = os.path.join(transcript_dir, 'original.backup.json')
            
            # 2. 读取现有的 original.json 内容
            original_content = {}
            if os.path.exists(original_path):
                try:
                    with open(original_path, 'r', encoding='utf-8') as f:
                        original_content = json.load(f)
                        # 如果还没有备份，创建备份
                        if not os.path.exists(backup_path):
                            ensure_dir(os.path.dirname(backup_path))
                            safe_write_json(backup_path, original_content)
                            logger.info("已创建原始文件备份")
                except Exception as e:
                    logger.error(f"读取原始文件失败: {str(e)}")
                    original_content = {"code": 200, "message": "success", "data": {}}
            else:
                original_content = {"code": 200, "message": "success", "data": {}}

            # 3. 确保data字段存在
            if "data" not in original_content:
                original_content["data"] = {}
            
            # 4. 获取原有segments数据
            original_data = original_content.get("data", {})
            original_segments = original_data.get("segments", [])
            
            # 5. 检查是否是第一次更新（通过检查第一个segment是否有subsegmentId）
            is_first_update = len(original_segments) > 0 and "subsegmentId" not in original_segments[0]
            
            # 6. 处理新的segments数据
            updated_segments = []
            segment = data.get("segments")  # 现在是字典
            
            # 从segment中获取subSegments
            for sub_segment in segment.get("subSegments", []):
                # 复制所有字段
                updated_segment = sub_segment.copy()
                
                # 如果是第一次更新
                if is_first_update:
                    matching_segment = next(
                        (s for s in original_segments 
                         if s.get("start_time") == sub_segment.get("start_time")),
                        None
                    )
                    if matching_segment:
                        # 保留原有字段，但允许新字段覆盖
                        updated_segment = {**matching_segment, **sub_segment}
                else:
                    # 使用subsegmentId匹配
                    matching_segment = next(
                        (s for s in original_segments 
                         if s.get("subsegmentId") == sub_segment.get("subsegmentId")),
                        None
                    )
                    if matching_segment:
                        # 保留原有字段，但允许新字段覆盖
                        updated_segment = {**matching_segment, **sub_segment}
                
                updated_segments.append(updated_segment)

            # 7. 更新content
            original_content["data"].update({
                "segments": updated_segments,
                "speakers": data.get("speakers", original_data.get("speakers", [])),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "full_text": "".join(segment["text"] for segment in updated_segments)
            })

            # 8. 保留其他原有字段
            for key in original_data:
                if key not in ["segments", "speakers", "updated_at"]:
                    original_content["data"][key] = original_data[key]  # full_text 在这里被保留了
            
            # 9. 保存更新后的内容
            if not safe_write_json(original_path, original_content):
                return {"code": 500, "message": "保存内容失败"}
            
            # 10. 更新metadata
            metadata_path = os.path.join(transcript_dir, 'metadata.json')
            current_metadata = {}
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        current_metadata = json.load(f)
                except Exception as e:
                    logger.error(f"读取metadata失败: {str(e)}")
            
            # 更新metadata
            current_metadata.update({
                'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'segments_count': len(updated_segments),
                'speakers_count': len(data.get('speakers', [])),
                'has_backup': True
            })
            
            if not safe_write_json(metadata_path, current_metadata):
                logger.warning("元数据更新失败")
            
            logger.info("文件内容保存成功")
            return {
                "code": 200,
                "message": "保存成功",
                "data": {
                    "file_id": file_id,
                    "updated_at": current_metadata['last_modified']
                }
            }
                
        except Exception as e:
            logger.error(f"保存文件内容失败: {str(e)}", exc_info=True)
            return {
                "code": 500,
                "message": f"保存失败: {str(e)}"
            }

# 创建全局实例
file_service = FileService(config.uploads_dir)