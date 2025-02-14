import sys
import os

# 添加server目录到Python路径
server_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, server_dir)

from server.api.speech.text_correction import TextCorrector
from server.api.logger import get_logger

logger = get_logger(__name__)

def test_correction():
    # 初始化文本纠正器
    corrector = TextCorrector()
    
    # 测试用例
    test_cases = [
        "本远",      # 应该纠正为"本源"
        "检查点",    # 应该纠正为"检测点"
        "心智控制取", # 应该纠正为"心智控制区"
        "第一令",    # 应该纠正为"第一灵"
        "正常文本",   # 不需要纠正
    ]
    
    logger.info("开始测试文本纠正...")
    for text in test_cases:
        corrected = corrector.correct_text(text)
        logger.info(f"原文本: {text}")
        logger.info(f"纠正后: {corrected}")
        logger.info("-" * 20)

if __name__ == "__main__":
    test_correction() 