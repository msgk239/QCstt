# api_service.py
from model_service import model  # 直接导入已初始化的模型
from funasr.utils.postprocess_utils import rich_transcription_postprocess

class APIService:
    def process_audio(self, audio_file):
        # 1. 直接使用全局model进行识别
        res = model.generate(
            input=audio_file,
            language="auto",
            vad_kwargs={"max_single_segment_time": 30000},
            spk_mode="vad_segment",
            spk_kwargs={
                "cb_kwargs": {"threshold": 0.5},
                "return_spk_res": True
            }
        )
        
        # 2. 处理说话人分离结果
        speakers_data = []
        for segment in res[0]["sentence_info"]:
            speaker_data = {
                "speaker": f"说话人{segment['speaker'][-1]}",
                "start_time": f"{segment['start']:.1f}",
                "end_time": f"{segment['end']:.1f}",
                "content": segment["sentence"]
            }
            speakers_data.append(speaker_data)
        
        # 3. 返回API响应
        return {
            "code": 200,
            "data": {
                "full_text": rich_transcription_postprocess(res[0]["text"]),
                "segments": speakers_data
            }
        }