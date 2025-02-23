import logging
logging.disable(logging.CRITICAL)  # 必须在导入 app 之前禁用日志

from .app import app
import uvicorn

def run_package():
    uvicorn.run(
        "server.api.app:app",
        host="0.0.0.0",
        port=8010,
        reload=False
    )

if __name__ == "__main__":
    run_package() 