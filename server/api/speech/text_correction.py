import os
from typing import List, Dict, Optional, Tuple
from ..logger import get_logger
import yaml
from pypinyin import pinyin, Style
import Levenshtein
import re
import time

logger = get_logger(__name__)

class TextCorrector:
    _instance = None
    _segmenter = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_file: str = "correction_config.yaml"):
        """初始化文本纠正器
        
        Args:
            config_file: 配置文件路径，包含目标词及其拼音信息
        """
        if hasattr(self, '_initialized'):
            return
            
        # 获取当前脚本所在目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.base_dir, config_file)
        # 存储格式: {word: (pinyin_list, context_words, threshold, original_words)}
        self.target_words: Dict[str, Tuple[List[str], List[str], float, List[str]]] = {}
        self.pinyin_cache = {}  # 缓存词语的拼音结果
        self.original_words_map = {}  # 新增：原词到目标词的映射
        
        # 初始化分词器
        self._init_segmenter()
        # 加载配置
        self.load_config()
        
        self._initialized = True

    def _should_update_dict(self) -> bool:
        """检查是否需要更新自定义词典
        
        Returns:
            bool: 是否需要更新
        """
        keywords_path = os.path.join(self.base_dir, "keywords")
        dict_path = os.path.join(self.base_dir, "custom_dict.txt")
        
        # 如果词典文件不存在，需要更新
        if not os.path.exists(dict_path):
            logger.info("自定义词典文件不存在，需要生成")
            return True
            
        # 比较修改时间
        keywords_mtime = os.path.getmtime(keywords_path)
        dict_mtime = os.path.getmtime(dict_path)
        
        needs_update = keywords_mtime > dict_mtime
        if needs_update:
            logger.info("keywords文件已更新，需要重新生成词典")
        return needs_update
        
    def _generate_custom_dict(self):
        """从keywords文件生成自定义词典"""
        logger.debug("开始生成自定义词典...")
        words = set()  # 存储目标词
        error_words = set()  # 存储错误识别的完整词组
        context_words = set()  # 存储上下文词
        keywords_path = os.path.join(self.base_dir, "keywords")
        
        def is_chinese_word(word: str) -> bool:
            """判断是否是有效的词
            
            规则：
            1. 纯英文词允许（比如 DNA）
            2. 中文词必须至少两个字，或一个字加数字/英文
            3. 不允许包含符号（包括标点符号）
            4. 不能全是数字
            """
            if not word or word.isspace():
                return False
            
            chinese_count = 0
            has_digit = False
            
            for c in word:
                if '\u4e00' <= c <= '\u9fa5':  # 中文字符
                    chinese_count += 1
                elif c.isdigit():  # 数字
                    has_digit = True
                elif not c.isalpha():  # 非字母的其他字符（符号）
                    return False
            
            # 纯英文词允许
            if word.isalpha():
                return True
            
            # 要么有至少两个中文字符，要么有一个中文字符加数字/英文
            return (chinese_count >= 2) or (chinese_count == 1 and (has_digit or any(c.isalpha() for c in word)))
        
        try:
            with open(keywords_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    # 提取所有可能的词
                    parts = line.split()
                    if not parts:
                        continue
                        
                    # 1. 添加目标词（第一个词）
                    target_word = parts[0]
                    if is_chinese_word(target_word):  # 确保是中文词
                        words.add(target_word)
                    
                    # 2. 处理后续部分
                    remaining = ' '.join(parts[1:])
                    
                    # 跳过数字（阈值）
                    if remaining and remaining[0].isdigit():
                        dot_idx = remaining.find('.')
                        if dot_idx != -1:
                            space_idx = remaining.find(' ', dot_idx)
                            if space_idx != -1:
                                remaining = remaining[space_idx+1:]
                            else:
                                continue
                    
                    # 3. 提取原词列表（支持中英文逗号）
                    if '(' in remaining:
                        word_part = remaining[:remaining.find('(')]
                    else:
                        word_part = remaining
                        
                    # 提取错误识别词组
                    error_parts = [w.strip() for w in word_part.replace('，', ',').split(',')]
                    for error_part in error_parts:
                        if is_chinese_word(error_part) and len(error_part) > 1:
                            error_words.add(error_part)
                    
                    # 4. 提取上下文词（在括号中的词）
                    context_match = re.search(r'\((.*?)\)', remaining)
                    if context_match:
                        context_parts = [w.strip() for w in context_match.group(1).replace('，', ',').split(',')]
                        for context_word in context_parts:
                            if is_chinese_word(context_word) and len(context_word) > 1:
                                context_words.add(context_word)
            
            # 保存词典文件
            dict_path = os.path.join(self.base_dir, "custom_dict.txt")
            
            # 过滤并按长度排序
            valid_words = sorted([w for w in words if len(w) > 1 and is_chinese_word(w)], 
                               key=len, reverse=True)
            valid_error_words = sorted([w for w in error_words if len(w) > 1 and is_chinese_word(w)], 
                                     key=len, reverse=True)
            valid_context_words = sorted([w for w in context_words if len(w) > 1 and is_chinese_word(w)], 
                                       key=len, reverse=True)
            
            # 写入词典，按顺序写入：目标词、错误词、上下文词
            with open(dict_path, 'w', encoding='utf-8') as f:
                # 写入目标词（按长度排序）
                for word in valid_words:
                    f.write(f"{word}\n")
                    
                # 写入错误词（按长度排序）
                for word in valid_error_words:
                    if word not in words:  # 避免重复
                        f.write(f"{word}\n")
                        
                # 写入上下文词（按长度排序）
                for word in valid_context_words:
                    if word not in words and word not in error_words:  # 避免重复
                        f.write(f"{word}\n")
                    
            logger.info(f"自定义词典生成完成，共{len(valid_words)}个目标词，{len(valid_error_words)}个错误词，{len(valid_context_words)}个上下文词")
            
        except Exception as e:
            logger.error(f"生成自定义词典失败: {str(e)}")
            raise
            
    def _init_segmenter(self):
        """初始化分词器"""
        if self._segmenter is not None:
            return
            
        try:
            # 检查是否需要更新词典
            if self._should_update_dict():
                self._generate_custom_dict()
                
            # 初始化分词器
            import pkuseg
            dict_path = os.path.join(self.base_dir, "custom_dict.txt")
            logger.debug("正在初始化分词器...")
            # 使用默认通用模型
            self._segmenter = pkuseg.pkuseg(user_dict=dict_path)
            logger.info("分词器初始化完成")
            
        except Exception as e:
            logger.error(f"初始化分词器失败: {str(e)}")
            self._segmenter = None  # 确保失败时设为None
            raise

    def _should_update_config(self) -> bool:
        """检查是否需要更新yaml配置文件
        
        Returns:
            bool: 是否需要更新
        """
        keywords_path = os.path.join(self.base_dir, "keywords")
        
        # 如果配置文件不存在，需要更新
        if not os.path.exists(self.config_file):
            logger.info("配置文件不存在，需要生成")
            return True
            
        # 比较修改时间
        keywords_mtime = os.path.getmtime(keywords_path)
        config_mtime = os.path.getmtime(self.config_file)
        
        needs_update = keywords_mtime > config_mtime
        if needs_update:
            logger.info("keywords文件已更新，需要重新生成配置")
        return needs_update

    def load_config(self) -> None:
        """从txt文件更新yaml配置文件，并加载配置"""
        try:
            # 检查是否需要更新配置
            if not self._should_update_config():
                # 直接从yaml加载配置
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {'target_words': {}}
                    
                # 加载配置到内存
                for word, info in config['target_words'].items():
                    pinyin_list = info.get('pinyin', [])
                    context_words = info.get('context_words', [])
                    threshold = info.get('similarity_threshold', 0.6)
                    orig_words = info.get('original_words', [])
                    self.target_words[word] = (pinyin_list, context_words, threshold, orig_words)
                    
                # 构建原词映射表
                for target_word, (_, _, _, orig_words) in self.target_words.items():
                    for orig in orig_words:
                        self.original_words_map[orig] = target_word
                
                logger.info(f"从配置文件加载了 {len(self.target_words)} 个目标词配置，{len(self.original_words_map)} 个原词映射")
                return
            
            def represent_list(dumper, data):
                return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
            yaml.add_representer(list, represent_list)
            
            keywords_file = os.path.join(self.base_dir, "keywords")
            keywords = []
            thresholds = {}  # 存储单独设置的阈值
            original_words = {}  # 存储原词映射
            context_words = {}  # 存储上下文词
            duplicate_words = {}  # 用于存储重复的词条
            
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line_number, line in enumerate(lines, 1):
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                            
                        # 提取上下文词（如果有）
                        context_list = []
                        if '(' in line and ')' in line:
                            context_start = line.find('(')
                            context_end = line.find(')')
                            if context_start < context_end:
                                context_part = line[context_start+1:context_end]
                                context_list = [w.strip() for w in context_part.split(',')]
                                # 移除上下文部分，处理剩余部分
                                line = line[:context_start].strip()
                        
                        # 分割剩余部分
                        parts = line.split(maxsplit=2)
                        if not parts:
                            continue
                            
                        word = parts[0]
                        threshold = 0.9  # 默认阈值
                        orig_words = []
                        
                        if len(parts) >= 2:
                            second_part = parts[1]
                            # 检查第二部分是否为阈值
                            try:
                                threshold = float(second_part)
                                # 如果有第三部分，那就是原词列表
                                if len(parts) == 3:
                                    orig_words = [w.strip() for w in parts[2].replace('，', ',').split(',')]
                            except ValueError:
                                # 如果不是阈值，就当作原词列表
                                orig_words = [w.strip() for w in second_part.replace('，', ',').split(',')]
                        
                        # 检查是否是重复的目标词
                        if word in keywords:
                            if word not in duplicate_words:
                                duplicate_words[word] = []
                                # 添加第一次出现的位置
                                first_line = next(i for i, l in enumerate(lines, 1) if l.strip().split(maxsplit=1)[0] == word)
                                duplicate_words[word].append((first_line, lines[first_line-1].strip()))
                            duplicate_words[word].append((line_number, line))
                            # 使用最大的阈值
                            if threshold > thresholds[word]:
                                thresholds[word] = threshold
                            # 合并原词列表
                            if orig_words:
                                if word not in original_words:
                                    original_words[word] = set()
                                original_words[word].update(orig_words)
                            # 合并上下文词
                            if context_list:
                                if word not in context_words:
                                    context_words[word] = set()
                                context_words[word].update(context_list)
                        else:
                            keywords.append(word)
                            thresholds[word] = threshold
                            if orig_words:
                                original_words[word] = set(orig_words)
                            if context_list:
                                context_words[word] = set(context_list)
            
            # 输出重复词条警告
            if duplicate_words:
                logger.warning("\n发现重复的目标词配置：")
                for word, occurrences in duplicate_words.items():
                    logger.warning(f"\n目标词 '{word}' 在以下行出现多次：")
                    for line_num, line_content in occurrences:
                        logger.warning(f"第 {line_num} 行: {line_content}")
                    logger.info(f"已自动合并配置：")
                    logger.info(f"- 使用最大阈值: {thresholds[word]}")
                    if word in original_words:
                        logger.info(f"- 合并后的原词数量: {len(original_words[word])}")
                    if word in context_words:
                        logger.info(f"- 合并后的上下文词数量: {len(context_words[word])}")
            
            # 准备yaml配置
            config = {'target_words': {}}
            
            # 更新配置
            for word in keywords:
                config['target_words'][word] = {
                    'pinyin': self.word_to_pinyin(word),
                    'context_words': list(context_words.get(word, set())),
                    'similarity_threshold': thresholds[word],
                    'original_words': list(original_words.get(word, set()))
                }
            
            # 保存更新后的配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            # 加载配置到内存
            for word, info in config['target_words'].items():
                pinyin_list = info.get('pinyin', [])
                context_words = info.get('context_words', [])
                threshold = info.get('similarity_threshold', 0.6)
                orig_words = info.get('original_words', [])
                self.target_words[word] = (pinyin_list, context_words, threshold, orig_words)
                
            # 构建原词映射表
            for target_word, (_, _, _, orig_words) in self.target_words.items():
                for orig in orig_words:
                    self.original_words_map[orig] = target_word
            
            logger.info(f"成功加载 {len(self.target_words)} 个目标词配置，{len(self.original_words_map)} 个原词映射")
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            self.target_words = {}

    def word_to_pinyin(self, word: str) -> List[str]:
        """将词转换为拼音列表
        
        Args:
            word: 待转换的词
            
        Returns:
            拼音列表
        """
        if word in self.pinyin_cache:
            return self.pinyin_cache[word]
            
        # 获取拼音（数字声调形式）
        py_list = [p[0] for p in pinyin(word, style=Style.TONE3)]
        self.pinyin_cache[word] = py_list
        return py_list

    def calculate_pinyin_similarity(self, py1: List[str], py2: List[str]) -> float:
        """计算两个拼音列表的相似度
        
        Args:
            py1: 第一个拼音列表
            py2: 第二个拼音列表
            
        Returns:
            相似度分数 (0-1)
        """
        if len(py1) != len(py2):
            return 0.0
            
        total_similarity = 0.0
        for p1, p2 in zip(py1, py2):
            # 使用Levenshtein距离计算单个拼音的相似度
            distance = Levenshtein.distance(p1, p2)
            max_len = max(len(p1), len(p2))
            similarity = 1 - (distance / max_len)
            total_similarity += similarity
            
        return total_similarity / len(py1)

    def find_best_match(self, word: str, context: str = "") -> Optional[tuple[str, float, float]]:
        """找到最匹配的目标关键词
        
        Returns:
            如果找到匹配，返回(匹配词, 相似度, 阈值)；否则返回None
        """
        # 如果输入词已经是目标词之一，直接返回None（无需替换）
        if word in self.target_words:
            return None
            
        word_pinyin = self.word_to_pinyin(word)
        best_match = None
        highest_similarity = 0
        matched_threshold = 0
        best_match_pinyin = None
        
        # 按词长分组，只比较相同长度的词
        for target_word, (target_pinyin, context_words, threshold, _) in self.target_words.items():
            # 检查词长是否相同
            if len(word) != len(target_word):
                continue
                
            # 计算拼音相似度
            similarity = self.calculate_pinyin_similarity(word_pinyin, target_pinyin)
            
            # 如果目标词有上下文要求，但上下文中没有任何一个上下文词，跳过这个匹配
            if context_words and not any(w in context for w in context_words):
                continue
                
            # 只有当相似度大于等于阈值时才更新最高相似度和匹配结果
            if similarity >= threshold and similarity > highest_similarity:
                highest_similarity = similarity
                best_match = target_word
                matched_threshold = threshold
                best_match_pinyin = target_pinyin
                logger.debug(f"找到相似度匹配: {word}({','.join(word_pinyin)}) -> {best_match}({','.join(target_pinyin)}) [相似度: {similarity:.3f}, 阈值: {threshold}]")
        
        # 如果找到最佳匹配，返回结果
        if best_match:
            return (best_match, highest_similarity, matched_threshold)
        
        return None

    def correct_text(self, text: str, context: str = "") -> str:
        """纠正文本中的词语
        
        Args:
            text: 待纠正的文本
            context: 上下文
            
        Returns:
            纠正后的文本
        """
        if not self.target_words:
            return text
            
        if not text or text.isspace():
            return text
            
        try:
            # 第一步：原词替换
            corrected_text = text
            replaced_positions = set()
            has_any_correction = False  # 记录是否发生任何纠正（包括原词替换和相似度匹配）
            
            # 按词长从长到短排序原词
            all_original_words = []
            for target_word, (_, context_words, _, orig_words) in self.target_words.items():
                for orig in orig_words:
                    if orig and not orig.isspace():
                        all_original_words.append((orig, target_word, context_words))
            all_original_words.sort(key=lambda x: len(x[0]), reverse=True)
            
            # 进行原词替换
            for orig_word, target_word, context_words in all_original_words:
                start = 0
                while True:
                    pos = corrected_text.find(orig_word, start)
                    if pos == -1:
                        break
                        
                    if not any(pos <= p < pos + len(orig_word) for p in replaced_positions):
                        if not context_words or any(w in text for w in context_words):
                            if orig_word != target_word:
                                has_any_correction = True
                                logger.info(f"原词替换: {orig_word} -> {target_word}")
                            corrected_text = corrected_text[:pos] + target_word + corrected_text[pos + len(orig_word):]
                            replaced_positions.update(range(pos, pos + len(target_word)))
                            
                    start = pos + 1
            
            # 第二步：分词和相似度匹配
            if self._segmenter is None:
                logger.warning("分词器未初始化，跳过相似度匹配")
                return corrected_text
                
            # 分词处理
            final_words = []
            current_pos = 0
            text_len = len(corrected_text)
            
            while current_pos < text_len:
                if current_pos in replaced_positions:
                    while current_pos < text_len and current_pos in replaced_positions:
                        final_words.append(corrected_text[current_pos])
                        current_pos += 1
                    continue
                
                end_pos = current_pos
                while end_pos < text_len and end_pos not in replaced_positions:
                    end_pos += 1
                
                if end_pos > current_pos:
                    segment = corrected_text[current_pos:end_pos]
                    words = self._segmenter.cut(segment)
                    logger.debug(f"分词: {' | '.join(words)}")
                    
                    for word in words:
                        if (word in '，。！？、；：""''（）【】《》' or 
                            len(word) == 1 or 
                            not word or 
                            word.isspace()):
                            final_words.append(word)
                            continue
                            
                        # 尝试相似度匹配
                        match_result = self.find_best_match(word, corrected_text)
                        if match_result:
                            best_match, similarity, threshold = match_result
                            target_context_words = self.target_words[best_match][1]
                            
                            if (not target_context_words or any(w in corrected_text for w in target_context_words)) and similarity >= threshold and word != best_match:
                                has_any_correction = True
                                word_pinyin = self.word_to_pinyin(word)
                                target_pinyin = self.word_to_pinyin(best_match)
                                logger.debug(f"执行相似度替换: {word}({','.join(word_pinyin)}) -> {best_match}({','.join(target_pinyin)}) [相似度: {similarity:.3f}, 阈值: {threshold}]")
                                final_words.append(best_match)
                                continue
                        
                        final_words.append(word)
                
                current_pos = end_pos
            
            result = ''.join(final_words)
            if has_any_correction:  # 只在发生了纠正时才输出最终结果
                logger.info(f"最终文本纠正: {text} -> {result}")
            return result
            
        except Exception as e:
            logger.error(f"文本纠正失败: {str(e)}")
            return text

    def correct_recognition_result(self, recognition_result: Dict) -> Dict:
        """纠正识别结果中的文本
        
        Args:
            recognition_result: 语音识别结果
            
        Returns:
            纠正后的识别结果
        """
        try:
            start_time = time.time()
            
            def extract_text(text: str) -> str:
                """从带标记的文本中提取纯文本部分
                
                Args:
                    text: 带标记的文本
                    
                Returns:
                    纯文本部分
                """
                # 找到第4个标记的结束位置
                pos = -1
                for i in range(4):
                    pos = text.find('|>', pos + 1)
                    if pos == -1:
                        return text  # 如果格式不对,返回原文本
                
                # 提取4个标记后到单引号前的文本
                text = text[pos + 2:].rstrip("'")
                return text
            
            # 处理每个句子片段
            all_text_parts = []
            if "sentence_info" in recognition_result[0]:
                for segment in recognition_result[0]["sentence_info"]:
                    if "sentence" in segment:
                        # 提取纯文本并纠正
                        text = extract_text(segment["sentence"])
                        # 使用分词器进行分词和纠正
                        if self._segmenter is None:
                            logger.warning("分词器未初始化，使用原始文本处理方式")
                            corrected_text = self._correct_text_without_segmenter(text)
                        else:
                            corrected_text = self.correct_text(text)
                            
                        # 替换原文本中的纯文本部分
                        original_sentence = segment["sentence"]
                        tags_end = original_sentence.find('>', original_sentence.rfind('<|')) + 1
                        corrected_sentence = original_sentence[:tags_end] + corrected_text
                        segment["sentence"] = corrected_sentence
                        all_text_parts.append(corrected_sentence)
            
            # 使用处理后的句子重建总文本
            if all_text_parts:
                # 使用原始格式拼接文本
                combined_text = '         '.join(all_text_parts)
                recognition_result[0]["text"] = combined_text
            
            end_time = time.time()
            logger.info(f"语音识别文本纠正完成，总耗时: {(end_time - start_time)*1000:.2f}ms")
            return recognition_result
            
        except Exception as e:
            logger.error(f"纠正识别结果失败: {str(e)}")
            return recognition_result

# 创建全局实例
text_corrector = TextCorrector()
