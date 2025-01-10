# 标准库
import json
import os
from typing import Optional
import time

# 第三方库
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse

# 本地模块
from .files.service import file_service
from .speech.recognize import speech_service
from .speech.storage import transcript_manager

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 开发服务器默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 文件管理 API
@app.get("/api/v1/files")
async def get_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: str = Query(None)
):
    return file_service.get_file_list(page, page_size, query)

@app.post("/api/v1/files/upload")
async def upload_file(
    file: UploadFile = File(...),
    options: str = Form(None)
):
    try:
        print(f"Receiving file: {file.filename}")
        # 读取文件内容
        contents = await file.read()
        print(f"File size: {len(contents)} bytes")
        
        # 解析选项
        upload_options = json.loads(options) if options else {}
        print(f"Upload options: {upload_options}")
        
        # 保存文件
        result = file_service.save_uploaded_file(contents, file.filename, upload_options)
        print(f"Save result: {result}")
        
        # 如果选择了自动识别，开始识别
        if result["code"] == 200 and upload_options.get("action") == "recognize":
            # TODO: 启动异步识别任务
            pass
        
        return result
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return {
            "code": 500,
            "message": f"上传失败: {str(e)}"
        }

@app.get("/api/v1/files/{file_id}")
async def get_file(file_id: str):
    return file_service.get_file_detail(file_id)

@app.delete("/api/v1/files/{file_id}")
async def delete_file(file_id: str):
    return file_service.delete_file(file_id)

@app.put("/api/v1/files/{file_id}")
async def update_file(file_id: str):
    # TODO: 实现文件更新
    pass

# 文件资源
@app.get("/api/v1/files/{file_id}/audio")
async def get_audio_file(file_id: str):
    try:
        # 获取文件路径
        file_info = file_service.get_file_path(file_id)
        if file_info["code"] != 200:
            return file_info
            
        file_path = file_info["data"]["path"]
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {
                "code": 404,
                "message": "文件不存在"
            }
            
        # 返回音频文件
        return FileResponse(
            path=file_path,
            filename=file_info["data"]["filename"],
            media_type="audio/wav"  # 根据实际文件类型设置
        )
        
    except Exception as e:
        print(f"Get audio file error: {str(e)}")
        return {
            "code": 500,
            "message": f"获取音频文件失败: {str(e)}"
        }

@app.get("/api/v1/files/{file_id}/path")
async def get_file_path(file_id: str):
    return file_service.get_file_path(file_id)

@app.put("/api/v1/files/{file_id}/rename")
async def rename_file(file_id: str, new_name: str = Form(...)):
    return file_service.rename_file(file_id, new_name)

@app.get("/api/v1/files/{file_id}/transcript")
async def get_transcript(file_id: str):
    return file_service.get_recognition_result(file_id)

@app.put("/api/v1/files/{file_id}/transcript")
async def update_transcript(file_id: str, data: dict):
    return file_service.save_recognition_result(file_id, data)

@app.delete("/api/v1/files/{file_id}/transcript")
async def delete_transcript(file_id: str):
    # TODO: 实现删除转写结果
    pass

# 2. 语音识别 API
@app.post("/api/v1/asr/recognize/{file_id}")
async def start_recognition(file_id: str):
    return file_service.start_recognition(file_id)

@app.get("/api/v1/asr/progress/{file_id}")
async def get_recognition_progress(file_id: str):
    return file_service.get_recognition_progress(file_id)

# 3. 回收站管理
@app.get("/api/v1/trash")
async def get_trash_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: str = Query(None)
):
    return file_service.get_trash_list(page, page_size, query)

@app.post("/api/v1/trash/{file_id}/restore")
async def restore_file(file_id: str):
    return file_service.restore_file(file_id)

@app.delete("/api/v1/trash/{file_id}")
async def permanently_delete_file(file_id: str):
    return file_service.permanently_delete_file(file_id)

@app.delete("/api/v1/trash")
async def clear_trash():
    return file_service.clear_trash()

# 4. 系统设置
@app.get("/api/v1/system/languages")
async def get_languages():
    return speech_service.get_languages()

@app.get("/api/v1/system/status")
async def get_system_status():
    # TODO: 实现系统状态获取
    pass

# 热词管理
@app.get("/api/v1/asr/hotwords")
async def get_hotwords():
    pass

@app.post("/api/v1/asr/hotwords")
async def add_hotword():
    pass

@app.put("/api/v1/asr/hotwords/{id}")
async def update_hotword():
    pass

@app.delete("/api/v1/asr/hotwords/{id}")
async def delete_hotword():
    pass

@app.post("/api/v1/asr/hotwords/batch-import")
async def batch_import_hotwords():
    pass

# 热词库管理
@app.get("/api/v1/asr/hotword-libraries")
async def get_hotword_libraries():
    pass

@app.post("/api/v1/asr/hotword-libraries")
async def create_hotword_library():
    pass

@app.put("/api/v1/asr/hotword-libraries/{id}")
async def update_hotword_library():
    pass

@app.delete("/api/v1/asr/hotword-libraries/{id}")
async def delete_hotword_library():
    pass

@app.post("/api/v1/asr/hotword-libraries/import")
async def import_hotword_library():
    pass

@app.get("/api/v1/asr/hotword-libraries/{id}/export")
async def export_hotword_library():
    pass

if __name__ == "__main__":
    uvicorn.run("server.api.app:app", host="0.0.0.0", port=8010, reload=True) 