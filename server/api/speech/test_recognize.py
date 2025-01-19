import os
import time
from ..logger import get_logger
from .recognize import SpeechService

logger = get_logger(__name__)

def test_languages():
    service = SpeechService()
    languages = service.get_languages()
    for lang in languages["data"]:
        pass

def test_asr():
    # 1. 初始化 Service
    service = SpeechService()
    
    # 2. 准备测试音频文件
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    test_file = os.path.join(root_dir, "input", "123456789.wav")
    
    # 3. 调用 Service 处理音频
    try:
        start_time = time.time()
        
        with open(test_file, "rb") as f:
            audio_data = f.read()
            result = service.process_audio(audio_data, "zh")  # 固定使用中文
        
        process_time = time.time() - start_time
        
        
    except Exception as e:
        raise e

if __name__ == "__main__":
    # 测试语言列表
    test_languages()
    
    # 只测试中文识别
    test_asr() 