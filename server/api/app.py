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
    start = time.time()
    result = file_service.get_file_list(page, page_size, query)
    print(f"API响应时间: {time.time() - start:.2f}秒")
    return result

# 获取单个文件详情
@app.get("/api/v1/files/{file_id}")
async def get_file(file_id: str):
    try:
        # 获取文件路径
        file_info = file_service.get_file_path(file_id)
        if file_info["code"] != 200:
            return file_info
            
        # 获取识别结果
        result = file_service.get_file_detail(file_id)
        if result["code"] == 200:
            result["data"].update({
                "path": file_info["data"]["path"],
                "filename": file_info["data"]["filename"]
            })
        
        return result
    except Exception as e:
        print(f"Get file detail error: {str(e)}")
        return {
            "code": 500,
            "message": f"获取文件详情失败: {str(e)}"
        }

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

# 重命名文件
@app.put("/api/files/{file_id}/rename")
async def rename_file(
    file_id: str,
    new_name: str = Form(...)  # 使用Form字段接收新文件名
):
    return file_service.rename_file(file_id, new_name)

# 添加获取文件路径的接口
@app.get("/api/files/{file_id}/path")
async def get_file_path(file_id: str):
    print(f"Getting path for file: {file_id}")  # 添加日志
    result = file_service.get_file_path(file_id)
    print(f"Path result: {result}")  # 添加日志
    return result  # FastAPI 会自动处理 JSON 序列化

# 添加开始识别的路由
@app.post("/api/v1/asr/recognize/{file_id}")
async def start_recognition(file_id: str):
    try:
        # 获取文件路径
        file_info = file_service.get_file_path(file_id)
        if file_info["code"] != 200:
            return file_info
            
        file_path = file_info["data"]["path"]
        
        # 读取音频文件
        with open(file_path, "rb") as f:
            audio_content = f.read()
            
        # 调用语音识别服务时传入 file_id
        recognition_result = speech_service.process_audio(
            audio_content,
            language="auto"
        )
        
        # 如果识别成功，更新文件状态
        if recognition_result["code"] == 200:
            file_service.update_file_status(file_id, "已完成")
            
        # 再保存结果
        if recognition_result["code"] == 200:
            transcript_manager.save_result(file_id, recognition_result)
        
        return recognition_result
        
    except Exception as e:
        print(f"Recognition error: {str(e)}")
        return {
            "code": 500,
            "message": f"识别失败: {str(e)}"
        }

# 添加获取识别进度的路由
@app.get("/api/v1/asr/progress/{file_id}")
async def get_recognition_progress(file_id: str):
    try:
        # TODO: 实现进度查询逻辑
        return {
            "code": 200,
            "message": "success",
            "data": {
                "progress": 100,  # 临时返回100%
                "status": "completed"
            }
        }
    except Exception as e:
        return {
            "code": 500,
            "message": f"获取进度失败: {str(e)}"
        }

# 添加获取音频文件的接口
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

if __name__ == "__main__":
    uvicorn.run("server.api.app:app", host="0.0.0.0", port=8010, reload=True) 