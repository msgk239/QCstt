# 通过环境变量设置设备，默认使用 cuda:0
# export SENSEVOICE_DEVICE=cuda:1

import os
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from enum import Enum
import torchaudio
import torch
from funasr import AutoModel
from funasr.utils.postprocess_utils import rich_transcription_postprocess
from io import BytesIO
from datetime import datetime
import re

# 获取项目根目录
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 如果没有设置环境变量，则使用本地缓存路径
if not os.getenv('MODELSCOPE_CACHE'):
    cache_dir = os.path.join(SCRIPT_DIR, ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.environ['MODELSCOPE_CACHE'] = os.path.join(cache_dir, "modelscope")
    os.environ['HF_HOME'] = os.path.join(cache_dir, "huggingface")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置常量
class Config:
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.flac', '.ogg'}
    CHUNK_SIZE = 1024 * 1024  # 1MB
    MODEL_DIR = "iic/SenseVoiceSmall"
    DEFAULT_DEVICE = os.getenv("SENSEVOICE_DEVICE", "cuda:0")

# 定义支持的语言枚举类
class Language(str, Enum):
    auto = "auto"     # 自动检测语言
    zh = "zh"         # 中文
    en = "en"         # 英文
    yue = "yue"       # 粤语
    ja = "ja"         # 日语
    ko = "ko"         # 韩语
    nospeech = "nospeech"  # 无语音

# 模型配置
try:
    # 初始化 ASR 模型
    model = AutoModel(
        model=Config.MODEL_DIR,
        trust_remote_code=True,      # 允许使用远程代码
        remote_code="./SenseVoice/model.py",    # 本地模型代码路径
        vad_model="fsmn-vad",       # 使用 FSMN-VAD 进行语音活动检测
        vad_kwargs={"max_single_segment_time": 30000},  # VAD 最大单段时长为 30s
        device=Config.DEFAULT_DEVICE  # 从配置获取设备配置
    )
except Exception as e:
    logger.error(f"模型加载失败: {str(e)}")
    raise

# 创建 FastAPI 应用
app = FastAPI(
    title="SenseVoice ASR API",
    description="语音识别服务 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 验证文件
def validate_audio_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )
    # 检查文件扩展名
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in Config.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。支持的格式: {', '.join(Config.ALLOWED_EXTENSIONS)}"
        )

# 根路由，返回简单的 HTML 页面
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset=utf-8>
            <title>SenseVoice ASR API</title>
        </head>
        <body>
            <h1>SenseVoice ASR API</h1>
            <p>这是一个语音识别服务 API</p>
            <a href='./docs'>API 文档</a>
        </body>
    </html>
    """

# 健康检查接口
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": os.getenv("SENSEVOICE_DEVICE", "cuda:0"),
        "timestamp": datetime.now().isoformat()
    }

# 获取支持的语言列表
@app.get("/languages")
async def get_languages():
    return {
        "code": 0,
        "message": "success",
        "result": [{"code": lang.value, "name": lang.name} for lang in Language]
    }

# ASR 接口：支持批量音频识别
@app.post("/api/v1/asr")
async def turn_audio_to_text(
    files: List[UploadFile] = File(...),
    language: Language = Language.auto
):
    try:
        results = []
        
        for file in files:
            try:
                # 验证文件
                validate_audio_file(file)
                
                # 保存临时文件
                temp_path = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}{os.path.splitext(file.filename)[1]}"
                with open(temp_path, "wb") as f:
                    contents = await file.read()
                    f.write(contents)
                
                try:
                    # 使用与 demo3.py 相同的参数调用模型
                    res = model.generate(
                        input=temp_path,
                        cache={},
                        language=language.value,  # 直接使用枚举值
                        use_itn=True,
                        batch_size_s=60,
                        merge_vad=True,
                        merge_length_s=15,
                    )
                    
                    if len(res) > 0:
                        result = {
                            "filename": file.filename,
                            "text": rich_transcription_postprocess(res[0]["text"]),
                            "raw_text": res[0]["text"],
                            "language": language.value
                        }
                    else:
                        result = {
                            "filename": file.filename,
                            "error": "识别结果为空"
                        }
                finally:
                    # 清理临时文件
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        
                results.append(result)
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "error": f"处理失败: {str(e)}"
                })
                
        return {
            "code": 0,
            "message": "success",
            "result": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        )

# 如果直接运行此文件，启动服务器
if __name__ == "__main__":
    import uvicorn
    # 启动服务器，host="0.0.0.0" 表示接受所有网络接口的连接
    uvicorn.run(app, host="0.0.0.0", port=8010)
