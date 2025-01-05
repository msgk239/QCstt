import os
import time
from api_service import APIService

def test_languages():
    print("\n=== 测试语言列表 API ===")
    api = APIService()
    languages = api.get_languages()
    print("支持的语言列表:")
    for lang in languages["data"]:
        print(f"- {lang['name']} ({lang['code']})")

def test_asr(language="auto"):
    # 1. 初始化 API Service
    api = APIService()
    
    # 2. 准备测试音频文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(current_dir, "input", "1234.wav")
    
    print(f"\n=== 开始测试 ASR API (语言: {language}) ===")
    print(f"测试文件: {test_file}")
    
    # 3. 调用 API 处理音频
    try:
        start_time = time.time()
        
        with open(test_file, "rb") as f:
            audio_data = f.read()
            result = api.process_audio(audio_data, language)
        
        process_time = time.time() - start_time
        print(f"处理耗时: {process_time:.2f}秒")
        
        # 4. 打印结果
        print("\n完整文本:")
        print(result["data"]["full_text"])
        
        print("\n分段信息:")
        for segment in result["data"]["segments"]:
            print(f"\n{segment['speaker_name']} ({segment['start_time']:.1f}s - {segment['end_time']:.1f}s):")
            print(f"文本: {segment['text']}")
            print("时间戳:", [f"{ts['start']:.1f}s-{ts['end']:.1f}s" for ts in segment['timestamps']])
        
        print("\n说话人列表:")
        for speaker in result["data"]["speakers"]:
            print(f"- {speaker['name']} (ID: {speaker['id']})")
        
        print("\n元数据:")
        print(f"- 音频时长: {result['data']['duration']:.2f}秒")
        print(f"- 识别语言: {result['data']['language']}")
        print("- 功能支持:", result["data"]["metadata"])
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        raise e

def run_all_tests():
    print("=== 开始全部测试 ===")
    
    # 测试语言列表
    test_languages()
    
    # 测试不同语言的识别
    for lang in ["auto", "zh", "en"]:
        test_asr(lang)
    
    print("\n=== 全部测试完成 ===")

if __name__ == "__main__":
    run_all_tests() 