from fastapi import HTTPException
import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from starlette.responses import FileResponse
from ..logger import get_logger
from .service import file_service
import json

logger = get_logger(__name__)

class ExportService:
    """导出服务类，处理不同格式的文件导出"""
    
    def __init__(self):
        self.supported_formats = {
            'word': self._export_to_word,
            'pdf': self._export_to_pdf,
            'txt': self._export_to_txt,
            'md': self._export_to_markdown,
            'srt': self._export_to_srt
        }
        # 创建导出文件的临时目录
        self.export_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'exports')
        os.makedirs(self.export_dir, exist_ok=True)
    
    async def handle_export_request(self, file_id: str, format: str) -> FileResponse:
        """
        处理导出请求
        Args:
            file_id: 文件ID
            format: 导出格式
        Returns:
            FileResponse: 文件响应
        """
        try:
            logger.info(f"导出文件 {file_id} 为 {format} 格式")
            
            # 获取转写数据
            transcript = file_service.get_recognition_result(file_id)
            #logger.info(f"获取到的转写数据: {transcript}")
            
            if transcript.get('code') != 200:
                raise HTTPException(status_code=400, detail="获取转写数据失败")
                
            # 使用导出服务处理导出
            file_path = self.export_transcript(file_id, format, transcript)
            logger.info(f"生成的文件路径: {file_path}")
            
            # 返回文件响应
            return FileResponse(
                path=file_path,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename=f"transcript.{format}",
                background=None
            )
                
        except Exception as e:
            logger.error(f"导出失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    def export_transcript(self, file_id: str, format: str, transcript_data: dict) -> str:
        """
        导出转写内容为指定格式
        Args:
            file_id: 文件ID
            format: 导出格式
            transcript_data: 转写数据
        Returns:
            str: 导出文件的路径
        """
        try:
            if format not in self.supported_formats:
                raise ValueError(f"不支持的导出格式: {format}")
                
            # 调用对应格式的导出方法
            export_func = self.supported_formats[format]
            return export_func(file_id, transcript_data)
            
        except Exception as e:
            logger.error(f"导出失败: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    def _export_to_word(self, file_id: str, data: dict) -> str:
        """
        导出为Word文档
        Args:
            file_id: 文件ID
            data: 转写数据，格式如 original.json
        Returns:
            str: 导出文件的路径
        """
        try:
            # 创建新的 Word 文档
            doc = Document()
            
            # 从根目录的 metadata.json 获取文件名
            metadata_path = os.path.join('storage', 'metadata.json')
            logger.info(f"metadata 文件路径: {metadata_path}")  # 添加日志
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                #logger.info(f"读取到的 metadata: {metadata}")  # 添加日志
            
            # 查找匹配的文件信息
            display_name = '转写文本'  # 默认标题
            for key in metadata:
                #logger.info(f"正在检查键: {key}")  # 添加日志
                if key.startswith(file_id):
                    file_info = metadata[key]
                    display_name = file_info['display_name']  # 直接获取 display_name
                    logger.info(f"找到匹配的文件名: {display_name}")  # 添加日志
                    break
            
            # 设置文档标题
            logger.info(f"最终使用的标题: {display_name}")  # 添加日志
            title = doc.add_heading(display_name, level=1)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 从 data 中获取实际的转写数据
            transcript_data = data.get('data', {}).get('data', {})
            segments = transcript_data.get('segments', [])
            
            # 合并连续的相同说话人的段落
            merged_segments = []
            current_segment = None
            
            for segment in segments:
                if not current_segment:
                    current_segment = {
                        'speakerDisplayName': segment['speakerDisplayName'],
                        'start_time': segment['start_time'],
                        'end_time': segment['end_time'],
                        'texts': [segment['text']]
                    }
                elif current_segment['speakerDisplayName'] == segment['speakerDisplayName']:
                    # 如果说话人相同，合并文本并更新结束时间
                    current_segment['texts'].append(segment['text'])
                    current_segment['end_time'] = segment['end_time']
                else:
                    # 说话人不同，保存当前段落并开始新段落
                    merged_segments.append(current_segment)
                    current_segment = {
                        'speakerDisplayName': segment['speakerDisplayName'],
                        'start_time': segment['start_time'],
                        'end_time': segment['end_time'],
                        'texts': [segment['text']]
                    }
            
            # 添加最后一个段落
            if current_segment:
                merged_segments.append(current_segment)
            
            # 将合并后的段落写入文档
            for segment in merged_segments:
                # 添加段落
                p = doc.add_paragraph()
                
                # 添加说话人名称（加粗）
                speaker_run = p.add_run(f"{segment['speakerDisplayName']}: ")
                speaker_run.bold = True
                
                # 添加时间戳（灰色小字）
                start_time = self._format_time(segment['start_time'])
                end_time = self._format_time(segment['end_time'])
                time_run = p.add_run(f"[{start_time} - {end_time}]")
                time_run.font.size = Pt(9)
                time_run.font.color.rgb = RGBColor(128, 128, 128)
                
                # 添加合并后的文本内容
                text_content = '\n'.join(segment['texts'])
                p.add_run(f"\n{text_content}\n")
            
            # 生成导出文件路径
            export_path = os.path.join(self.export_dir, f"{file_id}_transcript.docx")
            
            # 添加日志查看文档内容
            logger.info("准备保存的文档内容:")
            #for paragraph in doc.paragraphs:
                #logger.info(f"段落内容: {paragraph.text}")
            
            # 保存文档
            doc.save(export_path)
            #logger.info(f"Word文档导出成功: {export_path}")
            
            return export_path
            
        except Exception as e:
            logger.error(f"Word导出失败: {str(e)}", exc_info=True)
            raise Exception(f"Word导出失败: {str(e)}")
    
    def _format_time(self, seconds: float) -> str:
        """
        将秒数转换为时间字符串格式 (mm:ss)
        """
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def _export_to_pdf(self, file_id: str, data: dict) -> str:
        """导出为PDF文件"""
        # TODO: 实现PDF导出逻辑
        raise NotImplementedError("PDF导出功能尚未实现")
    
    def _export_to_txt(self, file_id: str, data: dict) -> str:
        """导出为纯文本文件"""
        # TODO: 实现TXT导出逻辑
        raise NotImplementedError("TXT导出功能尚未实现")
    
    def _export_to_markdown(self, file_id: str, data: dict) -> str:
        """导出为Markdown文件"""
        # TODO: 实现Markdown导出逻辑
        raise NotImplementedError("Markdown导出功能尚未实现")
    
    def _export_to_srt(self, file_id: str, data: dict) -> str:
        """导出为SRT字幕文件"""
        # TODO: 实现SRT导出逻辑
        raise NotImplementedError("SRT导出功能尚未实现")

# 创建全局实例
export_service = ExportService() 