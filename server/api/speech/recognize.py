from datetime import datetime
from typing import List, Dict, Optional
import os
import json
import shutil
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from .models import model

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
    
    def process_audio(self, audio_file: bytes, language: str = "auto") -> Dict:
        """处理音频文件，进行语音识别
        
        Args:
            audio_file: 音频文件的二进制数据
            language: 识别的目标语言，默认为自动检测
            
        Returns:
            包含识别结果的字典
        """
        # 1. 使用已正确配置的model进行识别
        res = model.generate(
            input=audio_file,
            output_timestamp=True,
            language=language,
            use_itn=True,
            batch_size_s=60
        )
        
        print("模型输出:", res)
        
        # 2. 处理说话人分离结果，格式化为飞书妙记风格
        speakers_data = []
        for segment in res[0]["sentence_info"]:
            # 移除标记符号并提取纯文本
            text = segment["sentence"]
            text = text.replace("<|zh|>", "").replace("<|NEUTRAL|>", "")
            text = text.replace("<|Speech|>", "").replace("<|withitn|>", "")
            text = text.replace("<|EMO_UNKNOWN|>", "")
            text = text.replace("<|SAD|>", "")
            
            speaker_data = {
                "speaker_id": f"speaker_{segment['spk']}",
                "speaker_name": f"说话人 {segment['spk'] + 1}",
                # 所有时间戳保留2位小数
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
        
        # 3. 构建识别结果
        recognition_result = {
            "code": 200,
            "message": "success",
            "data": {
                "duration": round(res[0].get("duration", 0), 2),
                "language": "zh",
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
                    "has_emotion": False
                }
            }
        }
        
        return recognition_result

# 创建全局实例
speech_service = SpeechService()
