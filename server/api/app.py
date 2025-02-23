# 标准库
import json
import os
from typing import Optional
import time

# 初始化日志配置（移到最前面）
from .logger import Logger
Logger.setup()
logger = Logger.get_logger(__name__)

# 第三方库
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Query, Request, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError

# 本地模块
from .files.service import file_service
from .speech.recognize import speech_service
from .speech.storage import transcript_manager
from .models import (
    BaseResponse,
    FileResponse, 
    FileListResponse,
    RecognitionProgressResponse
)
from .files.export import export_service  # 导入导出服务
from .speech.hotwords import hotwords_manager

# FastAPI 应用配置
app = FastAPI()

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 开发服务器默认端口
        "http://localhost:4173"   # Vite 预览服务器默认端口
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = [
        {
            'loc': ' -> '.join(str(loc) for loc in error['loc']),
            'msg': error['msg'],
            'type': error['type']
        }
        for error in exc.errors()
    ]
    logger.error(f"请求验证错误: {error_details}")
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "请求参数验证失败",
            "details": error_details
        }
    )

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"请求处理完成 - {request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"请求处理异常 - {request.method} {request.url} - {str(e)} - {process_time:.2f}s")
        raise

# 1. 文件管理 API
@app.get("/api/v1/files", response_model=FileListResponse)
async def get_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: str = Query(None)
):
    logger.info(f"获取文件列表 - 页码: {page}, 每页数量: {page_size}, 查询: {query}")
    return file_service.get_file_list(page, page_size, query)

@app.post("/api/v1/files/upload", response_model=FileResponse)
async def upload_file(
    file: UploadFile = File(...),
    options: str = Form(None)
):
    try:
        logger.info("=== 开始处理文件上传 ===")
        logger.debug("请求参数验证:")
        logger.debug(f"file 参数: {file}")
        logger.debug(f"options 参数: {options}")
        
        if not file:
            error_msg = "未接收到文件"
            logger.error(error_msg)
            return {"code": 422, "message": error_msg}
            
        logger.info(f"文件信息: 名称={file.filename}, 类型={file.content_type}, 大小={file.size if hasattr(file, 'size') else '未知'}")
        logger.debug(f"完整请求头: {dict(file.headers)}")
        logger.debug(f"上传选项: {options}")
        
        # 验证文件
        if not file.filename:
            error_msg = "文件名不能为空"
            logger.error(error_msg)
            return {"code": 400, "message": error_msg}
            
        # 读取文件内容
        try:
            logger.debug("开始读取文件内容...")
            contents = await file.read()
            file_size = len(contents)
            logger.info(f"文件读取完成, 大小: {file_size} bytes")
            
            if file_size == 0:
                error_msg = "文件内容为空"
                logger.error(error_msg)
                return {"code": 400, "message": error_msg}
                
        except Exception as e:
            error_msg = f"读取文件失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {"code": 400, "message": error_msg}
        
        # 解析选项
        try:
            upload_options = json.loads(options) if options else {}
            logger.debug(f"解析后的选项: {upload_options}")
        except json.JSONDecodeError as e:
            error_msg = f"选项格式错误: {str(e)}"
            logger.error(error_msg)
            return {"code": 400, "message": error_msg}
        
        # 保存文件
        logger.info("开始保存文件...")
        result = file_service.save_uploaded_file(contents, file.filename, upload_options)
        logger.info(f"文件保存结果: {result.get('code')} - {result.get('message')}")
        
        # 如果选择了自动识别，开始识别
        if result["code"] == 200 and upload_options.get("action") == "recognize":
            logger.info("启动自动识别任务...")
            # TODO: 启动异步识别任务
            pass
        
        logger.info("=== 文件上传处理完成 ===")
        return result
    except Exception as e:
        error_msg = f"上传失败: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "code": 500,
            "message": error_msg
        }

@app.get("/api/v1/files/{file_id}", response_model=FileResponse)
async def get_file(file_id: str):
    result = file_service.get_file_detail(file_id)
    return result

@app.delete("/api/v1/files/{file_id}", response_model=BaseResponse)
async def delete_file(file_id: str):
    logger.info(f"删除文件: {file_id}")
    return file_service.delete_file(file_id)

@app.put("/api/v1/files/{file_id}")
async def update_file(file_id: str, data: dict = Body(...)):
    logger.info(f"收到更新请求 - file_id: {file_id}")
    logger.info(f"请求数据类型: {type(data)}")  # 添加类型检查

    
    # 如果是字符串，尝试解析成字典
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return {"code": 400, "message": "数据格式错误"}
            
    return file_service.save_content(file_id, data)

# 文件资源
@app.get("/api/v1/files/{file_id}/audio")
async def get_audio_file(file_id: str):
    logger.info(f"=== 收到音频文件请求 === file_id: {file_id}")
    return file_service.get_audio_file(file_id)

@app.get("/api/v1/files/{file_id}/path", response_model=BaseResponse)
async def get_file_path(file_id: str):
    return file_service.get_file_path(file_id)

@app.put("/api/v1/files/{file_id}/rename", response_model=BaseResponse)
async def rename_file(file_id: str, new_name: str = Form(...)):
    return file_service.rename_file(file_id, new_name)

@app.get("/api/v1/files/{file_id}/transcript", response_model=FileResponse)
async def get_transcript(file_id: str):
    """获取转写内容的原始数据"""
    return file_service.get_recognition_result(file_id)

@app.get("/api/v1/files/{file_id}/transcript/export")
async def export_transcript(file_id: str, format: str = Query(..., description="导出格式(word/pdf/txt/md/srt)")):
    """
    导出转写内容为指定格式
    """
    return await export_service.handle_export_request(file_id, format)

@app.put("/api/v1/files/{file_id}/transcript", response_model=BaseResponse)
async def update_transcript(file_id: str, data: dict):
    return file_service.save_recognition_result(file_id, data)

@app.delete("/api/v1/files/{file_id}/transcript", response_model=BaseResponse)
async def delete_transcript(file_id: str):
    # TODO: 实现删除转写结果
    pass

# 2. 语音识别 API
@app.post("/api/v1/asr/recognize/{file_id}", response_model=BaseResponse)
async def start_recognition(file_id: str):
    return file_service.start_recognition(file_id)

@app.get("/api/v1/asr/progress/{file_id}", response_model=RecognitionProgressResponse)
async def get_recognition_progress(file_id: str):
    return file_service.get_recognition_progress(file_id)

# 3. 回收站管理
@app.get("/api/v1/trash", response_model=FileListResponse)
async def get_trash_files(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    query: str = Query(None)
):
    return file_service.get_trash_list(page, page_size, query)

@app.post("/api/v1/trash/{file_id}/restore", response_model=BaseResponse)
async def restore_file(file_id: str):
    return file_service.restore_file(file_id)

@app.delete("/api/v1/trash/{file_id}", response_model=BaseResponse)
async def permanently_delete_file(file_id: str):
    return file_service.permanently_delete_file(file_id)

@app.delete("/api/v1/trash", response_model=BaseResponse)
async def clear_trash():
    return file_service.clear_trash()

# 4. 系统设置
@app.get("/api/v1/system/languages", response_model=BaseResponse)
async def get_languages():
    return speech_service.get_languages()

@app.get("/api/v1/system/status", response_model=BaseResponse)
async def get_system_status():
    # TODO: 实现系统状态获取
    pass

# 热词管理
@app.get("/api/v1/hotwords")
async def get_hotwords():
    """获取热词内容"""
    return hotwords_manager.get_content()

@app.post("/api/v1/hotwords")
async def update_hotwords(data: dict = Body(...)):
    """更新热词内容"""
    logger.info("收到热词更新请求")
    #logger.debug(f"原始请求数据: {data}")
    
    content = data.get('content')
    last_modified = data.get('lastModified')
    
    #logger.debug(f"解析的内容: content={content}")
    logger.debug(f"解析的时间戳: lastModified={last_modified}")
    
    if not content:
        logger.error("内容为空")
        return {"code": 1, "message": "内容不能为空"}
        
    return hotwords_manager.update_content(content, last_modified)

@app.post("/api/v1/hotwords/validate")
async def validate_hotwords(data: dict = Body(...)):
    """验证热词格式"""
    content = data.get('content')
    
    if not content:
        return {"code": 1, "message": "内容不能为空"}
        
    return hotwords_manager.validate_content(content)

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

def standard_response(data=None, error=None, code=200):
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "data": data,
            "message": error
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "server.api.app:app", 
        host="0.0.0.0", 
        port=8010, 
        reload=True,
        access_log=True,
        use_colors=True,
        log_config=None  # 使用我们自己的日志配置
    ) 