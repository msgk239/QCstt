import os
from funasr import AutoModel

__all__ = ['model']

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
        
        self.model = AutoModel(
            model=os.path.join(SCRIPT_DIR, ".cache/modelscope/hub/iic/SenseVoiceSmall"),
            spk_model=os.path.join(SCRIPT_DIR, ".cache/modelscope/hub/iic/speech_campplus_sv_zh-cn_16k-common"),
            vad_model=os.path.join(SCRIPT_DIR, ".cache/modelscope/hub/iic/speech_fsmn_vad_zh-cn-16k-common-pytorch"),
            trust_remote_code=False,
            check_latest=False,  #禁用检查最新版本的模型
            local_files_only=True,  # 强制只使用本地缓存
            disable_update=True,  # 禁用 FunASR 版本检查
            remote_code=model_py_path,
            vad_kwargs={"max_single_segment_time": 30000},
            spk_mode="vad_segment",
            spk_kwargs={
                "cb_kwargs": {"merge_thr": 0.5},
                "return_spk_res": True
            },
            device="cpu",
            log_level="DEBUG",
            ncpu=6,
            batch_size=1
        )

        
        ModelService._instance = self

# 创建全局单例实例
model = ModelService.get_instance().model