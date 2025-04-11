from fastapi import HTTPException
import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from starlette.responses import FileResponse
from ..logger import get_logger
from .service import file_service
import json
import re

logger = get_logger(__name__)

class ExportService:
    """导出服务类，处理不同格式的文件导出"""
    
    def __init__(self):
        self.supported_formats = {
            'word': self._export_to_word,
            'pdf': self._export_to_pdf,
            'txt': self._export_to_txt,
            'md': self._export_to_markdown,
            'srt': self._export_to_srt,
            'rst': self._export_to_rst
        }
        # 创建导出文件的临时目录，设置为项目根目录下的exports
        self.export_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'exports')
        logger.info(f"导出目录设置为: {self.export_dir}")
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
            logger.info(f"开始导出文件 {file_id} 为 {format} 格式")
            
            # 获取转写数据
            transcript = file_service.get_recognition_result(file_id)
            #logger.debug(f"获取到的转写数据: {transcript}")
            
            if transcript.get('code') != 200:
                raise HTTPException(status_code=400, detail="获取转写数据失败")
                
            # 使用导出服务处理导出
            file_path = self.export_transcript(file_id, format, transcript)
            logger.info(f"导出成功，文件路径: {file_path}")
            
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
            logger.debug(f"读取 metadata 文件: {metadata_path}")  # 改为debug级别
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                #logger.debug(f"读取到的 metadata: {metadata}")  # 改为debug级别
            
            # 查找匹配的文件信息
            display_name = '转写文本'  # 默认标题
            for key in metadata:
                #logger.debug(f"正在检查键: {key}")  # 改为debug级别
                if key.startswith(file_id):
                    file_info = metadata[key]
                    display_name = file_info['display_name']  # 直接获取 display_name
                    logger.debug(f"找到匹配的文件名: {display_name}")  # 改为debug级别
                    break
            
            # 设置文档标题
            logger.debug(f"设置文档标题: {display_name}")  # 改为debug级别
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
            logger.debug("准备保存文档内容")  # 改为debug级别
            #for paragraph in doc.paragraphs:
                #logger.debug(f"段落内容: {paragraph.text}")  # 改为debug级别
            
            # 保存文档
            doc.save(export_path)
            logger.info(f"Word文档导出成功: {export_path}")  # 保留为info级别，这是关键信息
            
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
        """
        导出为SRT字幕文件
        Args:
            file_id: 文件ID
            data: 转写数据，格式如 original.json
        Returns:
            str: 导出文件的路径
        """
        try:
            # 从 data 中获取实际的转写数据
            transcript_data = data.get('data', {}).get('data', {})
            segments = transcript_data.get('segments', [])

            # 生成导出文件路径
            export_path = os.path.join(self.export_dir, f"{file_id}_transcript.srt")

            with open(export_path, 'w', encoding='utf-8') as srt_file:
                index = 1
                
                for segment in segments:
                    # 检查是否有子段落，前端可能会传入合并后的段落
                    if 'subSegments' in segment and segment['subSegments']:
                        # 使用子段落
                        for sub_segment in segment['subSegments']:
                            self._process_segment_to_srt(sub_segment, srt_file, index)
                            index += len(self._split_text(sub_segment.get('text', '')))
                    else:
                        # 使用主段落
                        self._process_segment_to_srt(segment, srt_file, index)
                        index += len(self._split_text(segment.get('text', '')))

            logger.info(f"SRT文档导出成功: {export_path}")
            return export_path

        except Exception as e:
            logger.error(f"SRT导出失败: {str(e)}", exc_info=True)
            raise Exception(f"SRT导出失败: {str(e)}")
            
    def _process_segment_to_srt(self, segment, srt_file, start_index):
        """
        处理一个段落并转换为SRT格式
        """
        # 检查是否有字级别的时间戳
        if 'timestamps' in segment and segment['timestamps'] and len(segment['timestamps']) > 0:
            # 处理字级别的时间戳
            self._process_with_char_timestamps(segment, srt_file, start_index)
        else:
            # 无字级别时间戳，使用段落级别的时间戳
            self._process_without_char_timestamps(segment, srt_file, start_index)
    
    def _process_with_char_timestamps(self, segment, srt_file, start_index):
        """
        使用字级别时间戳处理段落
        """
        timestamps = segment['timestamps']
        text = segment['text']
        
        # 分割文本并收集每一部分的时间戳
        parts = []
        current_part = ""
        part_start_time = None
        part_end_time = None
        
        for i, char in enumerate(text):
            # 获取当前字符的时间戳
            if i < len(timestamps):
                timestamp = timestamps[i]
                if part_start_time is None:
                    part_start_time = timestamp['start']
                part_end_time = timestamp['end']
            
            current_part += char
            
            # 当遇到标点符号或达到长度限制时，创建一个新部分
            if char in '。，' or len(current_part) >= 30:
                if current_part.strip() and part_start_time is not None and part_end_time is not None:
                    parts.append({
                        'text': current_part.strip(),
                        'start_time': part_start_time,
                        'end_time': part_end_time
                    })
                
                # 重置为下一个部分
                current_part = ""
                part_start_time = None if i + 1 < len(timestamps) else part_end_time
                part_end_time = None
        
        # 处理最后剩余的内容
        if current_part.strip() and part_start_time is not None and part_end_time is not None:
            parts.append({
                'text': current_part.strip(),
                'start_time': part_start_time,
                'end_time': part_end_time
            })
        
        # 写入SRT文件
        index = start_index
        for part in parts:
            srt_start = self._format_srt_time(part['start_time'])
            srt_end = self._format_srt_time(part['end_time'])
            srt_file.write(f"{index}\n")
            srt_file.write(f"{srt_start} --> {srt_end}\n")
            srt_file.write(f"{part['text']}\n\n")
            index += 1
    
    def _process_without_char_timestamps(self, segment, srt_file, start_index):
        """
        使用段落级别时间戳处理段落
        """
        start_time = self._format_srt_time(segment['start_time'])
        end_time = self._format_srt_time(segment['end_time'])
        text_content = segment['text']
        
        # 分割文本为多行
        lines = self._split_text(text_content)
        index = start_index
        
        for line in lines:
            if line.strip():  # 确保不写入空行
                srt_file.write(f"{index}\n")
                srt_file.write(f"{start_time} --> {end_time}\n")
                srt_file.write(f"{line.strip()}\n\n")
                index += 1
    
    def _format_srt_time(self, seconds: float) -> str:
        """
        将秒数转换为SRT时间字符串格式 (hh:mm:ss,ms)
        确保毫秒部分的精度准确
        """
        if seconds is None:
            seconds = 0.0
            
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds_value = seconds % 60
        # 保留整数部分和小数部分，确保毫秒的精度
        seconds_int = int(seconds_value)
        milliseconds = int(round((seconds_value - seconds_int) * 1000))
        
        return f"{hours:02}:{minutes:02}:{seconds_int:02},{milliseconds:03}"
    
    def _split_text(self, text: str, max_length: int = 30) -> list:
        """
        分割文本为多行，在逗号和句号处分割，同时保留标点符号，并限制每行的长度
        """
        # 使用正则表达式在标点符号后进行分割，但保留标点符号
        pattern = r'([。，])'
        parts = re.split(pattern, text)
        
        lines = []
        current_line = ""
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # 如果当前部分是标点符号
            if i + 1 < len(parts) and parts[i + 1] in '。，':
                punctuation = parts[i + 1]
                combined = part + punctuation
                
                # 如果添加这部分后长度超过限制，先添加当前行
                if current_line and len(current_line) + len(combined) > max_length:
                    lines.append(current_line)
                    current_line = combined
                else:
                    current_line += combined
                
                i += 2  # 跳过已处理的标点符号
            else:
                # 普通文本部分
                if current_line and len(current_line) + len(part) > max_length:
                    lines.append(current_line)
                    current_line = part
                else:
                    current_line += part
                i += 1
            
            # 如果当前部分以标点符号结尾，将其作为一个独立的行
            if current_line and current_line[-1] in '。，':
                lines.append(current_line)
                current_line = ""
        
        # 添加最后剩余的行
        if current_line:
            lines.append(current_line)
            
        return lines
    
    def _export_to_rst(self, file_id: str, data: dict) -> str:
        """
        导出为RST文件
        Args:
            file_id: 文件ID
            data: 转写数据，格式如 original.json
        Returns:
            str: 导出文件的路径
        """
        try:
            # 从 data 中获取实际的转写数据
            transcript_data = data.get('data', {}).get('data', {})
            segments = transcript_data.get('segments', [])

            # 生成导出文件路径
            export_path = os.path.join(self.export_dir, f"{file_id}_transcript.rst")

            with open(export_path, 'w', encoding='utf-8') as rst_file:
                # 写入标题
                rst_file.write(f"{file_id} 转写文本\n")
                rst_file.write("=" * len(f"{file_id} 转写文本") + "\n\n")

                # 写入每个段落
                for segment in segments:
                    speaker = segment['speakerDisplayName']
                    start_time = self._format_time(segment['start_time'])
                    end_time = self._format_time(segment['end_time'])
                    text_content = '\n'.join(segment['text'])

                    rst_file.write(f"{speaker} [{start_time} - {end_time}]\n")
                    rst_file.write(f"{text_content}\n\n")

            logger.info(f"RST文档导出成功: {export_path}")
            return export_path

        except Exception as e:
            logger.error(f"RST导出失败: {str(e)}", exc_info=True)
            raise Exception(f"RST导出失败: {str(e)}")

# 创建全局实例
export_service = ExportService() 