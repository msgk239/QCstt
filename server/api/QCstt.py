from .app import app
import uvicorn
from .logger import get_logger
import webbrowser
import threading
import time
import sys
import traceback

logger = get_logger(__name__)

def open_browser():
    """延迟2秒后打开浏览器"""
    try:
        time.sleep(2)
        webbrowser.open('http://localhost:8010')
    except Exception as e:
        logger.error(f"打开浏览器失败: {e}")

def run_prod():
    try:
        logger.info("启动生产环境服务...")
        # 创建一个线程来打开浏览器
        threading.Thread(target=open_browser, daemon=True).start()
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8010,
            reload=False,
            access_log=True,
            use_colors=True,
            log_config=None
        )
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        # 保持窗口不关闭
        input("按回车键退出...")

if __name__ == "__main__":
    try:
        run_prod()
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        input("按回车键退出...") 