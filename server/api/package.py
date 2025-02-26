import logging
logging.disable(logging.CRITICAL)  # 必须在导入 app 之前禁用日志

from .app import app
import uvicorn
import webbrowser
import threading
import time

def open_browser():
    """延迟2秒后打开浏览器"""
    try:
        time.sleep(2)
        webbrowser.open('http://localhost:8010')
    except Exception:
        pass

def run_package():
    # 创建一个线程来打开浏览器
    threading.Thread(target=open_browser, daemon=True).start()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8010,
        reload=False
    )

if __name__ == "__main__":
    run_package() 