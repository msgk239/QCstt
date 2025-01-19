import io
import logging
import numpy as np
import soundfile as sf
from pydub import AudioSegment

logger = logging.getLogger(__name__)

class AudioConverter:
    """音频格式转换工具类"""
    
    TARGET_SAMPLE_RATE = 16000
    TARGET_CHANNELS = 1
    TARGET_FORMAT = "wav"  # PCM 16bit
    
    @classmethod
    def convert_audio(cls, audio_bytes: bytes) -> bytes:
        """将输入音频转换为模型所需格式
        
        Args:
            audio_bytes: 输入音频的二进制数据
            
        Returns:
            转换后的音频二进制数据(WAV格式, 16kHz采样率, 单声道, 16bit PCM)
        """
        try:
            # 1. 加载音频
            audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
            
            # 2. 转换为单声道
            if audio.channels > 1:
                audio = audio.set_channels(cls.TARGET_CHANNELS)
                
            # 3. 重采样到16kHz
            if audio.frame_rate != cls.TARGET_SAMPLE_RATE:
                audio = audio.set_frame_rate(cls.TARGET_SAMPLE_RATE)
                
            # 4. 转换为16bit PCM WAV
            buffer = io.BytesIO()
            audio.export(buffer, format=cls.TARGET_FORMAT)
            
            logger.info(f"音频转换完成: {audio.channels}声道, {audio.frame_rate}Hz, {audio.sample_width*8}bit")
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"音频转换失败: {str(e)}", exc_info=True)
            raise RuntimeError(f"音频转换失败: {str(e)}") 