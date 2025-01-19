from datetime import datetime
from typing import List, Dict, Optional
import os
import json
import shutil
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from .models import model
import logging
import re
from .audio_utils import AudioConverter  # 添加导入

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
    
    def get_languages(self) -> Dict:
        """获取支持的语言列表"""
        return {
            "code": 200,
            "message": "success",
            "data": self.SUPPORTED_LANGUAGES
        }
    
    def process_audio(self, audio_file: bytes, language: str = "zh") -> Dict:
        """处理音频文件，进行语音识别
        
        Args:
            audio_file: 音频文件的二进制数据
            language: 识别的目标语言，默认为中文
            
        Returns:
            包含识别结果的字典
        """
        try:
            logger.info(f"=== 开始语音识别 ===")
            logger.info(f"输入参数 - 目标语言: {language}, 音频大小: {len(audio_file)} bytes")
            
            # 1. 音频格式转换
            logger.info("开始音频格式转换...")
            audio_file = AudioConverter.convert_audio(audio_file)
            logger.info(f"音频转换完成，转换后大小: {len(audio_file)} bytes")
            
            # 2. 使用已正确配置的model进行识别
            logger.info("开始调用模型进行识别...")
            res = model.generate(
                input=audio_file,
                output_timestamp=True,
                language=language,
                use_itn=True,
                batch_size_s=60
            )
            logger.info("模型识别完成")
            logger.debug(f"模型原始输出: {res}")
            
            # 2. 处理说话人分离结果，格式化为飞书妙记风格
            logger.info("开始处理说话人分离结果...")
            speakers_data = []
            for i, segment in enumerate(res[0]["sentence_info"]):
                logger.debug(f"处理第 {i+1} 个语音片段")
                # 移除标记符号并提取纯文本
                text = segment["sentence"]
                text = re.sub(r'<\|[^|]*\|>', '', text)
                
                speaker_data = {
                    "speaker_id": f"speaker_{segment['spk']}",
                    "speaker_name": f"说话人 {segment['spk'] + 1}",
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
                logger.debug(f"语音片段处理结果: {speaker_data}")
            
            # 3. 构建识别结果
            logger.info("开始构建最终识别结果...")
            recognition_result = {
                "code": 200,
                "message": "success",
                "data": {
                    "duration": round(res[0].get("duration", 0), 2),
                    "language": language,
                    "full_text": rich_transcription_postprocess(res[0]["text"]),
                    "segments": speakers_data,
                    "speakers": [
                        {
                            "id": f"speaker_{i}",
                            "name": f"说话人 {i + 1}"
                        } for i in set(seg['spk'] for seg in res[0]["sentence_info"])
                    ],
                    "metadata": {
                        "has_timestamp": True,
                        "has_speaker": True,
                        "has_emotion": True
                    }
                }
            }
            logger.info(f"语音识别完成，总时长: {recognition_result['data']['duration']}秒")
            logger.debug(f"最终识别结果: {recognition_result}")
            
            return recognition_result
            
        except Exception as e:
            logger.error(f"语音识别失败: {str(e)}", exc_info=True)
            return {
                "code": 500,
                "message": f"语音识别失败: {str(e)}"
            }

# 创建全局实例
speech_service = SpeechService()
