from .app import app
import uvicorn
from .logger import get_logger
import webbrowser
import threading
import time

logger = get_logger(__name__)

def open_browser():
    """延迟2秒后打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    webbrowser.open('http://localhost:8010')

def run_prod():
    logger.info("启动生产环境服务...")
    # 创建一个线程来打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(
        "server.api.app:app",
        host="0.0.0.0",
        port=8010,
        reload=False,
        access_log=True,
        use_colors=True,
        log_config=None
    )

if __name__ == "__main__":
    run_prod() 