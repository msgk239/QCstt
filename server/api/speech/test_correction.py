from .text_correction import text_corrector
from ..logger import get_logger

logger = get_logger(__name__)

def test_correction():
    # 基础测试
    text = "第13个的。有什么共性啊？嗯，反正就是大方向，整体上。你刚才那句没有听清楚呃呃什么有什么共性，什么东西啊？就这13个检测点有什么共性？你指的是D区里面这这个对吧？嗯。哦，一区的小点有什么共性？嗯，就是说这个整个区就刚才不说了吗？为什么把这13个点上点？嗯在这个工这个薪资控制区里边，嗯，好还是绵央区。"
    
    text_corrector.correct_text(text)

if __name__ == "__main__":
    test_correction() 