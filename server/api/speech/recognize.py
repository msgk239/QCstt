from typing import List, Dict
import os
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from .models import model
import logging
import re
from .audio_utils import AudioConverter  # 添加导入
from ..files.metadata import MetadataManager  # 添加导入
import time  # 添加这个导入
from .text_correction import text_corrector  # 导入文本纠正器实例

logger = logging.getLogger(__name__)

class SpeechService:
    """语音服务类，处理语音识别和语言支持"""
    
    # 添加支持的语言列表
    SUPPORTED_LANGUAGES: List[Dict[str, str]] = [
        {"code": "auto", "name": "自动检测"},
        {"code": "zh", "name": "中文"},
        {"code": "en", "name": "英文"},
        {"code": "ja", "name": "日语"},
        {"code": "ko", "name": "韩语"}
    ]
    
    def __init__(self):
        # 设置转写结果存储根目录
        self.transcripts_dir = os.path.join("storage", "transcripts")
        os.makedirs(self.transcripts_dir, exist_ok=True)
        self.metadata = MetadataManager()  # 添加 metadata 管理器
    
    def get_languages(self) -> Dict:
        """获取支持的语言列表"""
        return {
            "code": 200,
            "message": "success",
            "data": self.SUPPORTED_LANGUAGES
        }
    
    def process_audio(self, audio_file: bytes, language: str = "zh", file_id: str = None) -> Dict:
        """处理音频文件，进行语音识别
        
        Args:
            audio_file: 音频文件的二进制数据
            language: 识别的目标语言，默认为中文
            file_id: 音频文件ID，用于获取元数据
            
        Returns:
            包含识别结果的字典
        """
        start_time = time.perf_counter()  # 开始计时
        try:
            if not file_id:  # 检查是否有 file_id
                logger.error("缺少必要参数 file_id")
                return {
                    "code": 400,
                    "message": "缺少必要参数 file_id"
                }
            
            logger.info(f"=== 开始语音识别 ===")
            logger.info(f"输入参数 - 目标语言: {language}, 音频大小: {len(audio_file)} bytes, file_id: {file_id}")
            
            # 1. 音频格式转换
            logger.info("开始音频格式转换...")
            audio_file = AudioConverter.convert_audio(audio_file)
            logger.info(f"音频转换完成，转换后大小: {len(audio_file)} bytes")
            
            # 2. 使用已正确配置的model进行识别
            logger.info("开始调用模型进行识别...")
            recognition_start = time.perf_counter()  # 模型识别开始时间
            res = model.generate(
                input=audio_file,
                language=language,  # 语言参数默认中文
            )
            recognition_time = time.perf_counter() - recognition_start  # 计算模型识别时间
            logger.info(f"模型识别完成，识别耗时: {recognition_time:.2f}秒")
            #logger.debug(f"模型原始输出: {res}")

            # 调用文本纠正器对识别结果进行纠正
            logger.info("recognize:开始调用文本纠正器...")
            res = text_corrector.correct_recognition_result(res)
            logger.info("recognize:文本纠正完成")

            # 从元数据中获取音频时长
            metadata_prefix = f"metadata_{file_id}"
            logger.info(f"查找元数据，前缀: {metadata_prefix}")
            #logger.debug(f"当前元数据列表: {list(self.metadata.metadata.keys())}")  # 打印所有元数据键
            
            for key in self.metadata.metadata:
                if key.startswith(metadata_prefix):
                    metadata = self.metadata.get(key)
                    if metadata and metadata.get('duration'):
                        audio_duration = metadata['duration']
                        logger.info(f"从元数据获取到音频时长: {audio_duration}秒")
                        break
            else:  # 如果没找到
                logger.warning(f"未能从元数据获取到音频时长，metadata_prefix: {metadata_prefix}")
                audio_duration = res[0].get("duration", 0)
            
            # 2. 处理说话人分离结果，格式化为飞书妙记风格
            logger.info("开始处理说话人分离结果...")
            speakers_data = []
            colors = ['#409EFF', '#F56C6C']
            for i, segment in enumerate(res[0]["sentence_info"]):
                #logger.debug(f"处理第 {i+1} 个语音片段")
                # 移除标记符号并提取纯文本
                text = segment["sentence"]
                text = re.sub(r'<\|[^|]*\|>', '', text)
                
                speaker_data = {
                    "speaker_id": f"speaker_{segment['spk']}",
                    "speaker_name": f"说话人 {segment['spk'] + 1}",
                    "speakerKey": f"speaker_{segment['spk']}",
                    "speakerDisplayName": f"说话人 {segment['spk'] + 1}",
                    "color": colors[segment['spk'] % len(colors)],
                    "start_time": round(segment['start'] / 1000, 2),
                    "end_time": round(segment['end'] / 1000, 2),
                    "text": text.strip(),
                    "timestamps": [
                        {
                            "start": round(ts[0] / 1000, 2),
                            "end": round(ts[1] / 1000, 2)
                        } for ts in segment['timestamp']
                    ]
                }
                speakers_data.append(speaker_data)

            
            # 构建标准格式的 speakers
            speakers = [
                {
                    "speakerKey": f"speaker_{i}",
                    "speakerDisplayName": f"说话人 {i + 1}",
                    "color": colors[i % len(colors)],
                    "speaker_id": f"speaker_{i}",
                    "speaker_name": f"说话人 {i + 1}"
                } for i in set(seg['spk'] for seg in res[0]["sentence_info"])
            ]
            
            # 3. 构建识别结果
            logger.info("开始构建最终识别结果...")
            recognition_result = {
                "code": 200,
                "message": "success",
                "data": {
                    "duration": round(audio_duration, 2),  # 使用从元数据获取的时长
                    "language": language,
                    "full_text": rich_transcription_postprocess(res[0]["text"]),
                    "segments": speakers_data,
                    "speakers": speakers,  # 使用新的标准格式
                    "metadata": {
                        "has_timestamp": True,
                        "has_speaker": True,
                        "has_emotion": False
                    }
                }
            }
            logger.info(f"语音识别完成，总时长: {audio_duration}秒")  # 使用正确的时长
            
            total_time = time.perf_counter() - start_time  # 计算总处理时间
            logger.warning(f"语音识别完成，音频时长: {audio_duration:.2f}秒，总处理耗时: {total_time:.2f}秒，实时率: {audio_duration/total_time:.2f}x")
            
            # 在返回结果中添加处理时间信息
            recognition_result["data"]["process_info"] = {
                "total_time": round(total_time, 2),
                "recognition_time": round(recognition_time, 2),
                "rtf": round(audio_duration/total_time, 2)  # Real Time Factor
            }
            
            return recognition_result
            
        except Exception as e:
            logger.error(f"语音识别失败: {str(e)}", exc_info=True)
            return {
                "code": 500,
                "message": f"语音识别失败: {str(e)}"
            }

# 创建全局实例
speech_service = SpeechService()
