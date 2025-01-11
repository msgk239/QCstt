# 标准库导入
from typing import Dict
from ..logger import get_logger
import os

# 内部模块导入
from .config import config
from .metadata import MetadataManager
from .operations import FileOperations
from .trash import TrashManager

# 相关服务导入
from ..speech.storage import transcript_manager
from ..speech.recognize import speech_service
from ..utils import generate_target_filename, get_audio_metadata

logger = get_logger(__name__)

class FileService:
    """文件服务主类"""
    def __init__(self):
        self.config = config
        self.metadata = MetadataManager()
        self.operations = FileOperations()
        self.trash = TrashManager()
        self.uploads_dir = config.uploads_dir
    
    def save_uploaded_file(self, file_content, filename, options=None):
        """保存上传的文件，生成标准文件ID
        Args:
            file_content: 文件内容
            filename: 原始文件名
            options: 选项，包含language等
        """
        try:
            logger.info(f"=== 开始保存文件 ===")
            
            # 添加参数验证日志
            logger.debug("参数验证:")
            logger.debug(f"file_content 类型: {type(file_content)}, 大小: {len(file_content) if file_content else 0}")
            logger.debug(f"filename: {filename}")
            logger.debug(f"options: {options}")
            
            if not file_content:
                error_msg = "文件内容为空"
                logger.error(error_msg)
                return {"code": 422, "message": error_msg}
            
            if not filename:
                error_msg = "文件名为空"
                logger.error(error_msg)
                return {"code": 422, "message": error_msg}
            
            # 获取语言选项
            options = options or {}
            print(f"Service received options: {options}")
            
            options['original_filename'] = filename  # 添加原始文件名到选项中
            language = options.get('language', 'zh')
            logger.debug(f"识别语言: {language}")
            
            options['original_filename'] = filename
            logger.debug(f"处理后的选项: {options}")
            
            # 生成目标文件名
            target_filename, _, _, _ = generate_target_filename(filename)
            file_path = os.path.join(self.uploads_dir, target_filename)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # 获取音频元数据
            metadata_path = os.path.join(self.uploads_dir, 'metadata.json')
            metadata = get_audio_metadata(file_path, metadata_path)
            
            return {
                'code': 200,
                'message': '文件上传成功',
                'data': {
                    'file_id': target_filename,
                    'metadata': metadata
                }
            }
            
        except Exception as e:
            logger.error(f"保存上传文件失败: {str(e)}")
            return {
                'code': 500,
                'message': f'保存文件失败: {str(e)}'
            }
    
    def get_file_list(self, page: int, page_size: int, query: str = None):
        logger.info(f"获取文件列表 - 页码: {page}, 每页数量: {page_size}, 查询: {query}")
        return self.operations.get_file_list(page, page_size, query)
    
    def get_file_path(self, file_id):
        return self.operations.get_file_path(file_id)
    
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
            file_id: 原文件ID (timestamp_name.wav)
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
            print(f"\n=== 获取文件详情 ===")
            print(f"请求的文件ID: {file_id}")
            
            # 获取文件基本信息
            file_info = self.get_file_path(file_id)
            print(f"文件基本信息: {file_info}")
            
            if file_info["code"] != 200:
                return file_info
                
            file_path = file_info["data"]["path"]
            print(f"文件路径: {file_path}")
            
            # 获取转写结果
            print("\n获取转写结果...")
            transcripts = transcript_manager.get_transcript(file_id)
            print(f"转写结果: {transcripts}")
            
            print("\n获取元数据...")
            metadata = transcript_manager.get_metadata(file_id)
            print(f"元数据: {metadata}")
            
            # 构建响应
            status = metadata.get("status", "未识别") if metadata else "未识别"
            recognition_result = None
            
            # 检查转写结果
            if transcripts and "original" in transcripts:
                recognition_result = transcripts["original"]
                print(f"\n原始识别结果: {recognition_result}")
                # 如果original中包含data字段，则取data
                if isinstance(recognition_result, dict) and "data" in recognition_result:
                    recognition_result = recognition_result["data"]
                    print(f"处理后的识别结果: {recognition_result}")
                
            # 从元数据中获取原始文件名
            original_filename = metadata.get("original_filename") if metadata else file_id
            
            response = {
                "code": 200,
                "message": "success",
                "data": {
                    "id": file_id,
                    "name": original_filename,  # 使用原始文件名
                    "path": file_path,
                    "status": status,
                    "recognition_result": recognition_result,
                    "speech_type": metadata.get("language", "auto")  # 单独返回语音类型
                }
            }
            print(f"\n最终响应: {response}")
            return response
            
        except Exception as e:
            print(f"Get file detail error: {str(e)}")
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
                "data": transcripts["original"]
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
        # ...
        return {
            "filename": file.name,  # 返回原始文件名
            "speech_type": file.speech_type,  # 单独返回语音类型
            # ...
        }
    
    def start_recognition(self, file_id: str) -> Dict:
        """开始语音识别"""
        try:
            # 获取文件路径
            file_info = self.get_file_path(file_id)
            if file_info["code"] != 200:
                return file_info
                
            file_path = file_info["data"]["path"]
            
            # 读取音频文件
            with open(file_path, "rb") as f:
                audio_content = f.read()
            
            # 调用语音识别服务
            result = speech_service.process_audio(audio_content, "auto")
            
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

# 创建全局实例
file_service = FileService()