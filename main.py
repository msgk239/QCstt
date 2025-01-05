from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from api_service import APIService
import uvicorn

app = FastAPI()
api_service = APIService()

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
    return api_service.get_languages()

# 音频识别接口
@app.post("/api/recognize")
async def recognize_audio(
    file: UploadFile = File(...),
    language: str = "auto"
):
    contents = await file.read()
    result = api_service.process_audio(contents, language)
    return result

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8010, reload=True) 