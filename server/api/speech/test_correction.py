# 使用相对导入
from .text_correction import text_corrector
from ..logger import get_logger

logger = get_logger(__name__)

def test_correction():
    test_cases = [
        "本远",      # 应该纠正为"本源"
        "检查点",    # 应该纠正为"检测点"
        "心智控制取", # 应该纠正为"心智控制区"
        "第一令",    # 应该纠正为"第一灵"
        "正常文本",   # 不需要纠正
    ]
    
    logger.info("开始测试文本纠正...")
    for text in test_cases:
        corrected = text_corrector.correct_text(text)
        logger.info(f"原文本: {text}")
        logger.info(f"纠正后: {corrected}")
        logger.info("-" * 20)

if __name__ == "__main__":
    test_correction() 