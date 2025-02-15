from .text_correction import text_corrector
from ..logger import get_logger

logger = get_logger(__name__)

def test_correction():
    # 基本纠正测试
    basic_cases = [
        "本远",      # 应该纠正为"本源"
        "检查点",    # 应该纠正为"检测点"
        "心智控制取", # 应该纠正为"心智控制区"
        "第一名",    # 应该纠正为"第一灵"
        "整仓",      # 应该纠正为"整场"（原词匹配）
        "正常文本",   # 不应该纠正
        "第一令",    # 不应该纠正
    ]
    
    print("\n=== 基本纠正测试 ===")
    for text in basic_cases:
        corrected = text_corrector.correct_text(text)
        print(f"原文: {text} -> 纠正: {corrected}")
    
    # 上下文相关测试
    context_cases = [
        ("正常互催", "正常互催"),     # 有上下文词"互催"，应该纠正为"整场互催"
        ("正常工作", "正常工作"),     # 没有上下文词，不应该纠正
        ("整仓互催", "整仓互催"),     # 原词匹配，应该纠正为"整场互催"
        ("整仓工作", "整仓工作"),     # 原词匹配，应该纠正为"整场工作"
        ("正常互催下来", "正常互催下来"),  # 有上下文词"互催下来"，应该纠正为"整场互催下来"
    ]
    
    print("\n=== 上下文相关测试 ===")
    for text, context in context_cases:
        corrected = text_corrector.correct_text(text, context)
        print(f"原文: {text} (上下文: {context}) -> 纠正: {corrected}")
    
    # 长文本测试
    long_texts = [
        "今天工作很正常，一切都很顺利",  # 没有上下文词，不应该纠正"正常"
        "这场互催打得很正常，整场互催都很激烈",  # 有上下文词"互催"，应该纠正"正常"为"整场"
        "心智控制取的能量很强，第一令已经突破",  # 混合测试：原词匹配和相似度匹配
    ]
    
    print("\n=== 长文本测试 ===")
    for text in long_texts:
        corrected = text_corrector.correct_text(text, text)
        print(f"原文: {text}\n纠正: {corrected}\n")

if __name__ == "__main__":
    test_correction() 