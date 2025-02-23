from .app import app
import uvicorn
from .logger import get_logger

logger = get_logger(__name__)

def run_prod():
    logger.info("启动生产环境服务...")
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