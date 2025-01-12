from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# 基础响应模型
class BaseResponse(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="状态信息")

# 文件元数据模型
class FileMetadata(BaseModel):
    duration: Optional[float] = Field(0, description="音频时长(秒)")
    duration_str: Optional[str] = Field("00:00", description="格式化时长")
    # 可以根据需要在这里添加其他元数据字段

# 文件信息模型
class FileInfo(BaseModel):
    file_id: str = Field(..., description="文件ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文件元数据")

    class Config:
        schema_extra = {
            "example": {
                "file_id": "20250112_133516",
                "metadata": {
                    "duration": 0,
                    "duration_str": "00:00",
                    # metadata 可以包含以下字段：
                    # original_name: str - 原始文件名
                    # display_name: str - 显示名称
                    # display_full_name: str - 完整显示名称
                    # storage_name: str - 存储文件名
                    # extension: str - 文件扩展名
                    # size: int - 文件大小(字节)
                    # date: datetime - 上传时间
                    # status: str - 文件状态
                    # path: str - 文件路径
                    # options: Dict[str, Any] - 上传选项
                    # 以及其他任意元数据
                }
            }
        }

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