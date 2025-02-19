import os
import time
from typing import Dict, List, Tuple
from ..logger import get_logger
from .update_keywords import (
    merge_configs,      # 合并重复配置
    process_original_word,  # 处理原词
    is_pure_english,     # 检查英文
    read_keywords_file,   # 读取关键词文件
    update_keywords_file  # 更新关键词文件
)

logger = get_logger(__name__)

KEYWORDS_PATH = 'keywords'
BACKUP_PATH = 'keywords.backup'

class HotwordsManager:
    def __init__(self):
        self.keywords_path = KEYWORDS_PATH
        self.backup_path = BACKUP_PATH
        
    def get_content(self) -> Dict:
        """获取keywords文件内容和最后修改时间"""
        try:
            with open(self.keywords_path, 'r', encoding='utf-8') as f:
                content = f.read()
            last_modified = os.path.getmtime(self.keywords_path)
            return {
                'code': 0,
                'data': {
                    'content': content,
                    'lastModified': last_modified
                }
            }
        except Exception as e:
            logger.error(f"读取keywords文件失败: {str(e)}")
            return {'code': 1, 'message': f"读取文件失败: {str(e)}"}

    def update_content(self, content: str, last_modified: float = None) -> Dict:
        """更新keywords文件内容"""
        try:
            # 检查文件修改时间
            if last_modified is not None:
                current_mtime = os.path.getmtime(self.keywords_path)
                if abs(current_mtime - last_modified) > 0.001:
                    return {'code': 2, 'message': '文件已被其他人修改，请刷新后重试'}

            # 验证内容格式
            validation_result = self.validate_content(content)
            if not validation_result['data']['isValid']:
                return {'code': 3, 'message': '内容格式有误', 'errors': validation_result['data']['errors']}

            # 备份当前文件
            self._backup_file()

            # 解析内容并排序
            keywords_dict = read_keywords_file(content)
            word_mapping = {}  # 这里不需要词库映射
            
            # 使用 update_keywords_file 来处理排序和写入
            update_keywords_file(keywords_dict, word_mapping)

            return {'code': 0, 'message': '更新成功'}
        except Exception as e:
            logger.error(f"更新keywords文件失败: {str(e)}")
            return {'code': 1, 'message': f"更新失败: {str(e)}"}

    def validate_content(self, content: str) -> Dict:
        """验证内容格式"""
        errors = []
        keywords_dict = {}  # {目标词: [(行号, 阈值, 原词列表, 上下文词列表, 原始行)]}

        for line_num, line in enumerate(content.splitlines(), 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 1. 检查多余空格
            if '  ' in line:
                errors.append({
                    'line': line_num,
                    'message': '行中包含多余的空格',
                    'content': line
                })

            try:
                # 2. 提取上下文词（如果有）
                context_list = []
                if '(' in line:
                    if not ')' in line:
                        errors.append({
                            'line': line_num,
                            'message': '上下文括号不匹配',
                            'content': line
                        })
                        continue
                    context_start = line.find('(')
                    context_end = line.find(')')
                    if context_start > context_end:
                        errors.append({
                            'line': line_num,
                            'message': '上下文括号顺序错误',
                            'content': line
                        })
                        continue
                    context_part = line[context_start+1:context_end]
                    context_list = [w.strip() for w in context_part.split(',')]
                    line = line[:context_start].strip()

                # 3. 解析行内容
                parts = line.split(maxsplit=2)
                if not parts:
                    errors.append({
                        'line': line_num,
                        'message': '行格式错误',
                        'content': line
                    })
                    continue

                target_word = parts[0]
                threshold = None
                original_words = []

                if len(parts) >= 2:
                    # 检查第二部分是否为阈值
                    if any(c.isdigit() for c in parts[1]):
                        try:
                            threshold = float(parts[1])
                            if not 0 <= threshold <= 1:
                                errors.append({
                                    'line': line_num,
                                    'message': '阈值必须在0到1之间',
                                    'content': line
                                })
                            # 如果有第三部分，那就是原词列表
                            if len(parts) == 3:
                                original_words = [w.strip() for w in parts[2].replace('，', ',').split(',')]
                        except ValueError:
                            errors.append({
                                'line': line_num,
                                'message': '阈值格式错误',
                                'content': line
                            })
                    else:
                        original_words = [w.strip() for w in line[len(target_word):].strip().replace('，', ',').split(',')]

                # 4. 处理原词列表：去除空格，过滤纯英文
                original_words = [process_original_word(w) for w in original_words if not is_pure_english(w)]

                # 5. 记录配置
                if target_word not in keywords_dict:
                    keywords_dict[target_word] = []
                keywords_dict[target_word].append((line_num, threshold, original_words, context_list, line))

            except Exception as e:
                errors.append({
                    'line': line_num,
                    'message': f'解析错误: {str(e)}',
                    'content': line
                })

        # 6. 检查重复配置并合并
        duplicate_words = {}
        for word, configs in keywords_dict.items():
            if len(configs) > 1:
                duplicate_words[word] = configs
                # 尝试合并配置
                try:
                    merge_configs(configs)
                except Exception as e:
                    errors.append({
                        'line': configs[0][0],
                        'message': f'合并重复配置失败: {str(e)}',
                        'content': configs[0][4]
                    })

        # 7. 输出重复词条警告
        if duplicate_words:
            for word, occurrences in duplicate_words.items():
                first_line = occurrences[0][0]
                for line_num, _, _, _, _ in occurrences[1:]:
                    errors.append({
                        'line': line_num,
                        'message': f'重复的目标词，之前出现在第 {first_line} 行',
                        'content': word
                    })

        return {
            'code': 0,
            'data': {
                'isValid': len(errors) == 0,
                'errors': errors
            }
        }

    def _backup_file(self):
        """备份keywords文件"""
        try:
            if os.path.exists(self.keywords_path):
                with open(self.keywords_path, 'r', encoding='utf-8') as src:
                    with open(self.backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
        except Exception as e:
            logger.error(f"备份keywords文件失败: {str(e)}")
            raise

hotwords_manager = HotwordsManager() 