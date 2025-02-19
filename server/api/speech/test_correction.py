from .text_correction import text_corrector
from ..logger import get_logger

logger = get_logger(__name__)

def test_correction():
    texts = [
        # 单独测试林提的相似度
        "林提",
        "林提和灵体",
        
        # 实际对话场景测试
        "在心智控制取里面有一个检测点。",
        "主持人说要互催一下。",
        "这种意识转化的方式不对。",
        "古玲老师讲的很好。",
        "这个林提看起来很特别。",
        "前缀是什么意思？",
        "这个漏体状态不太好。",
        "找个春眠师调整一下。",
        "你看那个灵娥。"
    ]
    
    for text in texts:
        corrected = text_corrector.correct_text(text)
        print(f"原文: {text}")
        print(f"纠正: {corrected}\n")

if __name__ == "__main__":
    test_correction() 