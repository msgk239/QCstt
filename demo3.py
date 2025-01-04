import os
import datetime
import time
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess

# 获取当前脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SENSEVOICE_DIR = os.path.join(SCRIPT_DIR, "SenseVoice")

# 如果没有设置环境变量，则使用本地缓存路径
if not os.getenv('MODELSCOPE_CACHE'):
    cache_dir = os.path.join(SCRIPT_DIR, ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.environ['MODELSCOPE_CACHE'] = os.path.join(cache_dir, "modelscope")
    os.environ['HF_HOME'] = os.path.join(cache_dir, "huggingface")

print("开始加载模型...")
start_time = time.time()

model_dir = "iic/SenseVoiceSmall"
# 指定model.py的正确路径
model_py_path = os.path.join(SENSEVOICE_DIR, "model.py")
model = AutoModel(
    model=model_dir,
    trust_remote_code=True,
    remote_code=model_py_path,
    vad_model="fsmn-vad",
    vad_kwargs={"max_single_segment_time": 30000},
    device="cpu",  # 使用CPU
)

model_load_time = time.time() - start_time
print(f"模型加载完成，耗时：{model_load_time:.2f}秒")

print("开始识别音频...")
start_time = time.time()

# 使用os.path.join构建输入文件路径
input_file = os.path.join(SCRIPT_DIR, "input", "123.MP3")
res = model.generate(
    input=input_file,
    cache={},
    language="auto",  # "zn", "en", "yue", "ja", "ko", "nospeech"
    use_itn=True,
    batch_size_s=60,
    merge_vad=True,
    merge_length_s=15,
)
text = rich_transcription_postprocess(res[0]["text"])

process_time = time.time() - start_time
print(f"音频识别完成，耗时：{process_time:.2f}秒")

# 使用os.path.join构建输出目录路径
output_dir = os.path.join(SCRIPT_DIR, "shuchu")
os.makedirs(output_dir, exist_ok=True)

# 保存到文件（追加模式）
output_file = os.path.join(output_dir, "recognition_result.txt")
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
with open(output_file, "a", encoding="utf-8") as f:
    f.write(f"\n\n=== 识别时间：{current_time} ===\n")
    f.write(f"模型加载时间：{model_load_time:.2f}秒\n")
    f.write(f"音频处理时间：{process_time:.2f}秒\n")
    f.write(f"识别结果：\n{text}")

print(f"识别结果已追加到: {output_file}")