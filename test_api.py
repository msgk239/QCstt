import requests
import os
import subprocess
import time
import signal
import sys
import datetime
from funasr.utils.postprocess_utils import rich_transcription_postprocess

# API 基础URL
BASE_URL = "http://localhost:8010"
API_PROCESS = None

# 修改测试音频文件路径
AUDIO_FILE = os.path.join("input", "123.MP3")

# 添加这个到文件开头
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def start_api_server():
    """启动API服务器"""
    global API_PROCESS
    print("检查API服务器状态...")
    
    # 首先检查服务是否已经在运行
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("API服务器已经在运行！")
            return True
    except requests.exceptions.ConnectionError:
        # 服务未运行，继续启动流程
        print("API服务器未运行，准备启动...")
    
    # 如果服务未运行，则启动它
    print("正在启动API服务器...")
    api_script = os.path.join(os.path.dirname(__file__), "api2.py")
    
    API_PROCESS = subprocess.Popen([sys.executable, api_script])
    
    # 等待服务器启动
    for _ in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("API服务器已成功启动！")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    
    print("API服务器启动失败！")
    return False

def stop_api_server():
    """停止API服务器"""
    global API_PROCESS
    if API_PROCESS:
        print("正在停止API服务器...")
        # Windows下使用taskkill确保子进程也被终止
        if os.name == 'nt':
            subprocess.run(['taskkill', '/F', '/T', '/PID', str(API_PROCESS.pid)])
        else:
            API_PROCESS.terminate()
        API_PROCESS.wait()
        print("API服务器已停止！")

def test_health():
    """测试健康检查接口"""
    response = requests.get(f"{BASE_URL}/health")
    print("\n=== 健康检查测试 ===")
    print(response.json())
    assert response.status_code == 200

def test_languages():
    """测试获取支持语言列表"""
    response = requests.get(f"{BASE_URL}/languages")
    print("\n=== 支持语言测试 ===")
    print(response.json())
    assert response.status_code == 200

def test_file_upload():
    """测试文件上传识别"""
    try:
        if not os.path.exists(AUDIO_FILE):
            print(f"找不到测试音频文件: {AUDIO_FILE}")
            return
        
        print(f"音频文件路径: {AUDIO_FILE}")
        
        files = [
            ('files', (os.path.basename(AUDIO_FILE), open(AUDIO_FILE, 'rb'), 'audio/mpeg'))
        ]
        response = requests.post(
            f"{BASE_URL}/api/v1/asr",
            files=files,
            params={"language": "auto"}
        )
        
        print(f"API响应状态码: {response.status_code}")
        result = response.json()
        
        if response.status_code == 200:
            if result.get('code') == 0 and result.get('result'):
                text = result['result'][0]['text']
                save_recognition_result(text)
            else:
                print(f"错误：API返回异常 - {result.get('message', '未知错误')}")
        else:
            print(f"错误：HTTP状态码 {response.status_code}")
            
    except Exception as e:
        print(f"处理过程中出错: {str(e)}")
        raise

def format_recognition_result(text):
    """格式化识别结果文本
    - 保留原始标记
    - 按句号分段
    """
    # 按句号分段
    paragraphs = text.split('。')
    # 过滤空段落并格式化
    formatted_paragraphs = []
    for p in paragraphs:
        if p.strip():  # 只处理非空段落
            formatted_paragraphs.append(p.strip() + '。')
    
    # 使用两个换行符连接段落
    return '\n\n'.join(formatted_paragraphs)

def save_recognition_result(result):
    """保存识别结果到文件"""
    try:
        # 使用绝对路径
        output_dir = os.path.join(SCRIPT_DIR, "shuchu")
        output_file = os.path.join(output_dir, "recognition_result.txt")
        
        print(f"保存目录: {output_dir}")
        print(f"保存文件: {output_file}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"准备写入的文本长度: {len(str(result))}")
        print(f"文本前100个字符: {str(result)[:100]}")
        
        # 添加格式化处理
        formatted_result = format_recognition_result(result)
        
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n=== 识别时间：{current_time} ===\n")
            f.write(f"识别结果：\n{formatted_result}\n")
            f.write("-" * 50 + "\n")
        
        print(f"文件写入成功: {output_file}")
        
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")
        print(f"当前工作目录: {os.getcwd()}")
        raise

def main():
    """运行所有测试"""
    try:
        # 启动API服务器
        if not start_api_server():
            print("无法启动API服务器，测试终止！")
            return

        # 检查音频文件是否存在
        if not os.path.exists(AUDIO_FILE):
            print(f"错误：找不到测试音频文件 {AUDIO_FILE}")
            return

        print("\n开始API测试...")
        test_health()
        test_languages()
        test_file_upload()
        print("\n所有测试完成!")

    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    
    # 移除这部分，不再自动停止API服务器
    # finally:
    #     stop_api_server()

if __name__ == "__main__":
    # 修改信号处理，不再自动停止
    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))
    main() 