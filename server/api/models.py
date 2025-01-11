from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# 基础响应模型
class BaseResponse(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="状态信息")

# 文件信息模型
class FileInfo(BaseModel):
    id: str = Field(..., description="文件ID")
    original_name: str = Field(..., description="原始文件名")
    display_name: str = Field(..., description="显示名称")
    display_full_name: str = Field(..., description="完整显示名称")
    storage_name: str = Field(..., description="存储文件名")
    extension: str = Field(..., description="文件扩展名")
    size: int = Field(..., description="文件大小(字节)")
    date: datetime = Field(..., description="上传时间")
    status: str = Field(..., description="文件状态")
    path: str = Field(..., description="文件路径")
    duration: Optional[float] = Field(None, description="音频时长(秒)")
    duration_str: Optional[str] = Field(None, description="格式化时长")
    options: Optional[Dict[str, Any]] = Field(None, description="上传选项")

# 文件响应模型
class FileResponse(BaseResponse):
    data: FileInfo

# 文件列表响应模型
class FileListResponse(BaseResponse):
    data: Dict[str, Any] = Field(..., description="响应数据")
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {
                    "items": [],
                    "total": 0,
                    "page": 1,
                    "page_size": 20
                }
            }
        }

# 识别进度响应模型
class RecognitionProgressResponse(BaseResponse):
    data: Dict[str, Any] = Field(..., description="识别进度信息")
    class Config:
        schema_extra = {
            "example": {
                "code": 200,
                "message": "success", 
                "data": {
                    "progress": 75,
                    "status": "processing",
                    "message": "正在识别..."
                }
            }
        } 