import os
from funasr import AutoModel

class ModelService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        if ModelService._instance is not None:
            raise Exception("This class is a singleton!")
            
        # 获取当前脚本所在目录的绝对路径
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
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
            model=model_dir,
            trust_remote_code=False,
            remote_code=model_py_path,
            vad_model="fsmn-vad",
            vad_kwargs={"max_single_segment_time": 30000},
            spk_model="cam++",
            spk_mode="vad_segment",
            spk_kwargs={
                "cb_kwargs": {"merge_thr": 0.5},
                "return_spk_res": True
            },
            device="cpu",
            disable_update=True,
            log_level="DEBUG",
            ncpu=4,
            batch_size=1
        )

        
        ModelService._instance = self

# 创建全局单例实例
model = ModelService.get_instance().model