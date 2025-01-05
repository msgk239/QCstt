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
    # 1. 模型加载相关
    trust_remote_code=False,
    remote_code=model_py_path,
    
    # 2. VAD 相关
    vad_model="fsmn-vad",
    vad_kwargs={
        "max_single_segment_time": 30000
    },
    
    # 3. 说话人相关
    spk_model="cam++",
    spk_mode="vad_segment",
    spk_kwargs={
        "cb_kwargs": {
            "merge_thr": 0.5
        },
        "return_spk_res": True
    },
    
    # 4. 运行环境相关
    device="cpu",
    disable_update=True,
    log_level="DEBUG",
    
    # 5. 性能相关
    ncpu=4,  # CPU线程数
    batch_size=1  # CPU模式下建议为1
)

model_load_time = time.time() - start_time
print(f"模型加载完成，耗时：{model_load_time:.2f}秒")

print("开始识别音频...")
start_time = time.time()

# 使用os.path.join构建输入文件路径
input_file = os.path.join(SCRIPT_DIR, "input", "1234.wav")

# 在 generate 前添加
print("\n=== 调试信息 - 输入参数 ===")
print("generate参数:", {
    "output_timestamp": True,
    "spk_mode": "vad_segment",
    "vad_kwargs": {"max_single_segment_time": 30000},
    "spk_kwargs": {
        "cb_kwargs": {"merge_thr": 0.5},
        "return_spk_res": True
    }
})

res = model.generate(
    output_timestamp=True,
    input=input_file,
    language="auto",
    use_itn=True,
    batch_size_s=60
)

print("\n=== 调试信息 - VAD 和说话人分割 ===")
print("1. VAD 结果:")
if len(res) > 0:
    print("- value:", res[0].get("value", []))
    if "value" in res[0]:
        print("- value 类型:", type(res[0]["value"]))
        print("- value 长度:", len(res[0]["value"]))
        if len(res[0]["value"]) > 0:
            print("- 第一个分段:", res[0]["value"][0])

print("\n2. 时间戳信息:")
if len(res) > 0:
    print("- timestamp 存在:", "timestamp" in res[0])
    print("- timestamp:", res[0].get("timestamp", []))
    if "timestamp" in res[0]:
        print("- timestamp 类型:", type(res[0]["timestamp"]))
        print("- timestamp 长度:", len(res[0]["timestamp"]))

print("\n3. 文本信息:")
if len(res) > 0:
    print("- text 存在:", "text" in res[0])
    print("- text:", res[0].get("text", ""))

print("\n4. 说话人信息:")
if len(res) > 0:
    print("- sentence_info 存在:", "sentence_info" in res[0])
    print("- sentence_info:", res[0].get("sentence_info", []))
    if "sentence_info" in res[0]:
        print("- sentence_info 类型:", type(res[0]["sentence_info"]))
        print("- sentence_info 长度:", len(res[0]["sentence_info"]))

print("\n5. 完整结果键值:")
if len(res) > 0:
    print("- 所有键:", res[0].keys())
    for key in res[0].keys():
        print(f"- {key} 类型:", type(res[0][key]))

print("\n6. 模型配置:")
print("- spk_model 存在:", model.spk_model is not None)
print("- spk_mode:", model.spk_mode if hasattr(model, "spk_mode") else "未设置")
print("- vad_model 存在:", model.vad_model is not None)
print("- punc_model 存在:", model.punc_model is not None)

# 原有的处理逻辑
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

print("返回结果:", res)
if len(res) > 0:
    print("时间戳:", "timestamp" in res[0])
    print("结果内容:", res[0].keys())