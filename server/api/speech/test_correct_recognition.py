from .text_correction import text_corrector
from ..logger import get_logger

logger = get_logger(__name__)

def test_correct_recognition_result():
    # 模拟语音识别结果
    recognition_result = [
        {
            "key": "rand_key_2yW4Acq9GFz6Y",
            "text": "<|zh|><|NEUTRAL|><|Speech|><|withitn|>我们先看一下心智控制取这边的情况。         <|zh|><|NEUTRAL|><|Speech|><|withitn|>主持人刚才讲到这个意识转化的问题，我觉得需要互催一下。         <|zh|><|NEUTRAL|><|Speech|><|withitn|>古玲老师说这个林提状态不太好，建议找个春眠师调整。         <|zh|><|NEUTRAL|><|Speech|><|withitn|>前缀是什么意思我还不太明白，不过漏体确实需要处理。         <|zh|><|NEUTRAL|><|Speech|><|withitn|>灵娥说的这些问题都很重要。",
            "sentence_info": [
                {
                    "start": 0,
                    "end": 630,
                    "sentence": "<|zh|><|NEUTRAL|><|Speech|><|withitn|>我们先看一下心智控制取这边的情况。",
                    "timestamp": [[0, 570], [570, 630]],
                    "spk": 0
                },
                {
                    "start": 1740,
                    "end": 2430,
                    "sentence": "<|zh|><|NEUTRAL|><|Speech|><|withitn|>主持人刚才讲到这个意识转化的问题，我觉得需要互催一下。",
                    "timestamp": [[1740, 2070], [2070, 2430]],
                    "spk": 0
                },
                {
                    "start": 2430,
                    "end": 3030,
                    "sentence": "<|zh|><|NEUTRAL|><|Speech|><|withitn|>古玲老师说这个林提状态不太好，建议找个春眠师调整。",
                    "timestamp": [[2430, 3030]],
                    "spk": 0
                },
                {
                    "start": 3030,
                    "end": 3630,
                    "sentence": "<|zh|><|NEUTRAL|><|Speech|><|withitn|>前缀是什么意思我还不太明白，不过漏体确实需要处理。",
                    "timestamp": [[3030, 3630]],
                    "spk": 0
                },
                {
                    "start": 3630,
                    "end": 4230,
                    "sentence": "<|zh|><|NEUTRAL|><|Speech|><|withitn|>灵娥说的这些问题都很重要。",
                    "timestamp": [[3630, 4230]],
                    "spk": 0
                }
            ]
        }
    ]

    # 调用 correct_recognition_result 方法进行纠正
    text_corrector.correct_recognition_result(recognition_result)

if __name__ == "__main__":
    test_correct_recognition_result() 