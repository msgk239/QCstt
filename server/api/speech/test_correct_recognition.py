from .text_correction import text_corrector
from ..logger import get_logger

logger = get_logger(__name__)

def test_correct_recognition_result():
    # 模拟语音识别结果
    recognition_result = [
        {
            "text": "本远是一个检查点",
            "sentence_info": [
                {"sentence": "本远"},
                {"sentence": "是一个"},
                {"sentence": "检查点"}
            ]
        },
        {
            "text": "心智控制取需要第一令",
            "sentence_info": [
                {"sentence": "心智控制取"},
                {"sentence": "需要"},
                {"sentence": "第一令"}
            ]
        }
    ]

    # 调用 correct_recognition_result 方法进行纠正
    text_corrector.correct_recognition_result(recognition_result)

if __name__ == "__main__":
    test_correct_recognition_result() 