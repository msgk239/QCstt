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
from datetime import datetime
import shutil

logger = get_logger(__name__)

KEYWORDS_PATH = 'keywords'
BACKUP_PATH = 'keywords.backup'

class HotwordsManager:
    def __init__(self, keywords_path=None, backup_path=None):
        """初始化热词管理器
        
        Args:
            keywords_path (str, optional): keywords文件路径. 默认为None
            backup_path (str, optional): 备份文件路径. 默认为None
        """
        # 获取 server 目录的绝对路径
        server_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # 使用绝对路径
        self.keywords_path = keywords_path or os.path.join(server_dir, 'api', 'speech', 'keywords')
        self.backup_dir = backup_path or os.path.join(server_dir, 'api', 'speech', 'backups')
        
        # 确保备份目录存在
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        # 迁移旧的备份文件（如果存在）
        old_backup = os.path.join(os.path.dirname(self.keywords_path), 'keywords.backup')
        if os.path.exists(old_backup):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_backup = os.path.join(self.backup_dir, f'keywords_{timestamp}.backup')
            shutil.copy2(old_backup, new_backup)
            logger.info(f"已迁移旧备份文件到: {new_backup}")

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
                if abs(current_mtime - last_modified) > 0.001:  # 添加一个小的容差
                    return {'code': 2, 'message': '文件已被其他人修改，请刷新后重试'}

            # 验证内容格式
            validation_result = self.validate_content(content)
            if not validation_result['data']['isValid']:
                return {'code': 3, 'message': '内容格式有误', 'errors': validation_result['data']['errors']}

            # 备份当前文件
            self._backup_file()

            # 解析内容并排序
            keywords_dict = {}
            for line in content.splitlines():
                if line.strip():
                    # 转换中文标点为英文标点
                    line = line.strip().replace('，', ',').replace('（', '(').replace('）', ')')
                    parts = line.split(' ', 2)
                    if len(parts) >= 2:
                        target_word = parts[0]
                        keywords_dict[target_word] = line

            # 写入排序后的内容
            with open(self.keywords_path, 'w', encoding='utf-8') as f:
                for target_word in sorted(keywords_dict.keys()):
                    f.write(f"{keywords_dict[target_word]}\n")

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
        """备份keywords文件，使用时间戳命名"""
        try:
            if not os.path.exists(self.keywords_path):
                logger.warning("keywords文件不存在，跳过备份")
                return

            # 生成带时间戳的备份文件名（不使用微秒）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f'keywords_{timestamp}.backup'
            backup_path = os.path.join(self.backup_dir, backup_filename)

            # 使用 shutil 复制文件（更安全的文件复制方式）
            shutil.copy2(self.keywords_path, backup_path)
            
            # 保留最近10个备份，删除更早的备份
            self._cleanup_old_backups()
            
            logger.info(f"已创建备份: {backup_filename}")

        except Exception as e:
            logger.error(f"备份keywords文件失败: {str(e)}")
            raise

    def _cleanup_old_backups(self, keep_count=10):
        """清理旧的备份文件，只保留最近的 keep_count 个备份"""
        try:
            # 获取所有备份文件
            backup_files = [f for f in os.listdir(self.backup_dir) 
                          if f.startswith('keywords_') and f.endswith('.backup')]
            
            # 按文件名排序（因为文件名包含时间戳）
            backup_files.sort(reverse=True)  # 文件名中的时间戳格式保证了按名字排序等同于按时间排序
            
            # 删除多余的备份
            for old_file in backup_files[keep_count:]:
                old_path = os.path.join(self.backup_dir, old_file)
                os.remove(old_path)
                logger.debug(f"已删除旧备份: {old_file}")

        except Exception as e:
            logger.error(f"清理旧备份失败: {str(e)}")
            # 清理失败不影响主流程，所以这里不抛出异常

hotwords_manager = HotwordsManager() 