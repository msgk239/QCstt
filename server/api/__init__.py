# 标准库
import json
import os
from typing import Optional

# 第三方库
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware

# 本地模块
from .files.service import file_service
from .speech.recognize import speech_service

app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue dev server 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取支持的语言列表
@app.get("/api/languages")
async def get_languages():
    return speech_service.get_languages()

# 文件上传接口
@app.post("/api/files/upload")
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

# 获取文件列表
@app.get("/api/files")
async def get_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: str = Query(None)
):
    return file_service.get_file_list(page, page_size, query)

# 删除文件
@app.delete("/api/files/{file_id}")
async def delete_file(file_id: str):
    return file_service.delete_file(file_id)

# 音频识别接口
@app.post("/api/recognize")
async def recognize_audio(
    file: UploadFile = File(...),
    language: str = "auto"
):
    contents = await file.read()
    result = speech_service.process_audio(contents, language)
    return result

# 获取回收站文件列表
@app.get("/api/trash")
async def get_trash_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: str = Query(None)
):
    return file_service.get_trash_list(page, page_size, query)

# 从回收站恢复文件
@app.post("/api/trash/{file_id}/restore")
async def restore_file(file_id: str):
    return file_service.restore_file(file_id)

# 永久删除文件
@app.delete("/api/trash/{file_id}")
async def permanently_delete_file(file_id: str):
    return file_service.permanently_delete_file(file_id)

# 清空回收站
@app.delete("/api/trash")
async def clear_trash():
    return file_service.clear_trash()

if __name__ == "__main__":
    uvicorn.run("server.api:app", host="0.0.0.0", port=8010, reload=True) 