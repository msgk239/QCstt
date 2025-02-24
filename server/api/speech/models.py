import os
from funasr import AutoModel
import torch
import logging
import psutil  # 添加这个导入来获取更详细的CPU信息

__all__ = ['model']

logger = logging.getLogger(__name__)

class ModelService:
    """语音识别模型服务类，提供单例模型实例"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls) -> 'ModelService':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if ModelService._instance is not None:
            raise Exception("This class is a singleton!")
            
        # 获取项目根目录的绝对路径
        SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        SENSEVOICE_DIR = os.path.join(SCRIPT_DIR, "SenseVoice")
        
        # 设置缓存路径
        if not os.getenv('MODELSCOPE_CACHE'):
            cache_dir = os.path.join(SCRIPT_DIR, ".cache")
            os.makedirs(cache_dir, exist_ok=True)
            os.environ['MODELSCOPE_CACHE'] = os.path.join(cache_dir, "modelscope")
            os.environ['HF_HOME'] = os.path.join(cache_dir, "huggingface")


        model_dir = "iic/SenseVoiceSmall"
        model_py_path = os.path.join(SENSEVOICE_DIR, "model.py")
        
        # 检测设备和CPU核心数
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        physical_cores = psutil.cpu_count(logical=False)  # 获取物理核心数
        
        # 获取基本系统信息
        cpu_info = {
            "物理CPU核心数": physical_cores
        }
        
        # 打印系统信息
        logger.info("=== 系统资源信息 ===")
        for key, value in cpu_info.items():
            logger.info(f"{key}: {value}")
        
        # 根据设备类型设置参数
        if device == "cuda:0":
            # GPU模式下的配置
            config = {
                "device": device,
                "batch_size_s": 60,  
                "log_level": "INFO",
                "vad_kwargs": {
                    "max_single_segment_time": 60000  # 默认是30秒，这里设置为60秒    
                },
                            # 模型推理配置
                "cache": {},                # 每次调用使用新的缓存
                "output_timestamp": True,   # 输出时间戳信息
                "use_itn": True,           # 启用标点符号和数字的文本正则化
                "ban_emo_unk": True       # 禁用情感标签
            }
            logger.info("=== GPU模式配置 ===")
            logger.info(f"使用GPU模式")
            logger.info(f"CUDA是否可用: {torch.cuda.is_available()}")
            logger.info(f"GPU设备名称: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU显存总量: {torch.cuda.get_device_properties(0).total_memory / 1024**2:.0f}MB")
        else:
            # CPU模式下的配置
            recommended_cpu = max(1, physical_cores - 1)
            config = {
                "device": device,
                "batch_size_s": 60,  # CPU模式下会被强制为单个处理
                "ncpu": recommended_cpu,  # CPU模式下有效
                "log_level": "INFO",
                "vad_kwargs": {
                    "max_single_segment_time": 60000  # 默认是30秒，这里设置为60秒
                },
                # 模型推理配置
                "cache": {},                # 每次调用使用新的缓存
                "output_timestamp": True,   # 输出时间戳信息
                "use_itn": True,           # 启用标点符号和数字的文本正则化
                "ban_emo_unk": True       # 禁用情感标签
            }
            logger.info("=== CPU模式配置 ===")
            logger.info(f"使用CPU模式")
            logger.info(f"物理核心数: {physical_cores}")
            logger.info(f"建议使用的核心数: {recommended_cpu} (物理核心数-1)")
        
        self.model = AutoModel(
            # 模型路径配置
            model=os.path.join(SCRIPT_DIR, ".cache/modelscope/hub/iic/SenseVoiceSmall"),  # 主模型路径
            spk_model=os.path.join(SCRIPT_DIR, ".cache/modelscope/hub/iic/speech_campplus_sv_zh-cn_16k-common"),  # 说话人分离模型
            vad_model=os.path.join(SCRIPT_DIR, ".cache/modelscope/hub/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch"),  # 语音活动检测模型
            
            # 性能优化配置
            trust_remote_code=False,    # 使用内部集成版本，而不是远程代码
            check_latest=False,         # 禁用检查最新版本的模型
            local_files_only=True,      # 强制只使用本地缓存的模型文件
            disable_update=True,        # 禁用 FunASR 版本检查
            remote_code=model_py_path,  # 指定模型代码路径
            
            # 说话人分离配置
            spk_mode="vad_segment",     # 基于VAD切分的说话人分离模式
            spk_kwargs={
                "cb_kwargs": {"merge_thr": 0.5},  # 说话人聚类的阈值
                "return_spk_res": True   # 返回说话人分离结果
            },
            
            # 动态配置参数
            **config  # 包含device(设备)、batch_size_s(批处理大小)、ncpu(CPU核心数)、log_level(日志级别)
        )

        
        ModelService._instance = self

# 创建全局单例实例
model = ModelService.get_instance().model