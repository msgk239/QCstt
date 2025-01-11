from ..logger import get_logger
logger = get_logger(__name__)

class FileStorage:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        ensure_dir(base_dir)
        
    def save_file(self, file_content, file_id, metadata=None):
        """保存文件
        Args:
            file_content: 文件内容
            file_id: 文件ID (timestamp_filename.wav)
            metadata: 文件元数据，包含原始文件名等信息
        """
        try:
            logger.info(f"保存文件: {file_id}")
            # 确保文件名格式正确
            if not self._validate_file_id(file_id):
                logger.error(f"无效的文件ID: {file_id}")
                return {
                    "code": 400,
                    "message": "文件ID格式不正确"
                }
            
            # 构建完整路径
            file_path = os.path.join(self.base_dir, file_id)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(file_content)
                
            # 保存元数据
            if metadata:
                self._save_metadata(file_id, metadata)
                
            return {
                "code": 200,
                "message": "success",
                "data": {
                    "file_id": file_id,
                    "path": file_path
                }
            }
            
        except Exception as e:
            print(f"Save file error: {str(e)}")
            return {
                "code": 500,
                "message": f"保存文件失败: {str(e)}"
            }
            
    def _validate_file_id(self, file_id):
        """验证文件ID格式
        格式: YYYYMMDD_HHMMSS_filename.wav
        """
        try:
            # 检查基本格式
            if not file_id or '_' not in file_id:
                return False
            
            # 分离时间戳和文件名
            timestamp = '_'.join(file_id.split('_')[:2])  # 获取完整时间戳 YYYYMMDD_HHMMSS
            
            # 验证时间戳格式
            datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            
            return True
            
        except ValueError:
            return False
            
    def _save_metadata(self, file_id, metadata):
        """保存文件元数据"""
        metadata_path = os.path.join(self.base_dir, f"{file_id}.meta.json")
        safe_write_json(metadata_path, metadata) 