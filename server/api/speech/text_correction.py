import os
from typing import List, Dict, Optional, Tuple
from ..logger import get_logger
import yaml
from pypinyin import pinyin, Style
import Levenshtein

logger = get_logger(__name__)

class TextCorrector:
    def __init__(self, config_file: str = "correction_config.yaml"):
        """初始化文本纠正器
        
        Args:
            config_file: 配置文件路径，包含目标词及其拼音信息
        """
        # 获取当前脚本所在目录
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_file = os.path.join(self.base_dir, config_file)
        # 存储格式: {word: (pinyin_list, context_words, threshold, original_words)}
        self.target_words: Dict[str, Tuple[List[str], List[str], float, List[str]]] = {}
        self.pinyin_cache = {}  # 缓存词语的拼音结果
        self.original_words_map = {}  # 新增：原词到目标词的映射
        self.load_config()

    def load_config(self) -> None:
        """从txt文件更新yaml配置文件，并加载配置"""
        try:
            def represent_list(dumper, data):
                return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
            yaml.add_representer(list, represent_list)
            
            keywords_file = os.path.join(self.base_dir, "keywords")
            keywords = []
            thresholds = {}  # 存储单独设置的阈值
            original_words = {}  # 存储原词映射
            context_words = {}  # 存储上下文词
            
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    for line in f:
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
                        threshold = 0.6  # 默认阈值
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
                        
                        keywords.append(word)
                        thresholds[word] = threshold
                        if orig_words:
                            original_words[word] = orig_words
                        if context_list:
                            context_words[word] = context_list
            
            # 准备yaml配置
            config = {'target_words': {}}
            
            # 如果已存在yaml配置，先读取它
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    existing_config = yaml.safe_load(f) or {'target_words': {}}
            else:
                existing_config = {'target_words': {}}
            
            # 更新配置
            for word in keywords:
                if word not in existing_config['target_words']:
                    config['target_words'][word] = {
                        'pinyin': self.word_to_pinyin(word),
                        'context_words': context_words.get(word, []),
                        'similarity_threshold': thresholds[word],
                        'original_words': original_words.get(word, [])
                    }
                else:
                    # 完全更新配置
                    config['target_words'][word] = {
                        'pinyin': self.word_to_pinyin(word),
                        'context_words': context_words.get(word, []),
                        'similarity_threshold': thresholds[word],
                        'original_words': original_words.get(word, [])
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
        # 先检查原词映射表（最高优先级）
        if word in self.original_words_map:
            target = self.original_words_map[word]
            # 获取目标词的阈值
            _, _, threshold, _ = self.target_words[target]
            return (target, 1.0, threshold)

        word_pinyin = self.word_to_pinyin(word)
        best_match = None
        highest_similarity = 0
        matched_threshold = 0
        
        for target_word, (target_pinyin, context_words, threshold, orig_words) in self.target_words.items():
            # 检查是否是原词之一（最高优先级）
            if word in orig_words:
                return (target_word, 1.0, threshold)
                
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
            
        # 如果输入为空或者只包含空白字符，直接返回
        if not text or text.isspace():
            return text
            
        try:
            # 先检查完整文本是否在原词映射表中
            if text in self.original_words_map:
                target = self.original_words_map[text]
                if text != target:  # 只在实际发生纠正时记录日志
                    logger.info(f"纠正: {text} -> {target}")
                return target
            
            # 尝试完整匹配
            match_result = self.find_best_match(text, context)
            if match_result:
                best_match, similarity, threshold = match_result
                if similarity >= threshold and text != best_match:  # 只在实际发生纠正时记录日志
                    logger.info(f"纠正: {text} -> {best_match}")
                    return best_match
            
            # 分词并纠正
            corrected_words = []
            i = 0
            
            while i < len(text):
                # 如果是标点符号，直接添加并继续
                if text[i] in '，。！？、；：""''（）【】《》':
                    corrected_words.append(text[i])
                    i += 1
                    continue
                
                # 获取所有可能的词长度，从长到短排序
                possible_lengths = sorted(set(
                    len(word) for word in list(self.original_words_map.keys()) + list(self.target_words.keys())
                ), reverse=True)
                
                matched = False
                for length in possible_lengths:
                    if i + length > len(text):
                        continue
                        
                    current_word = text[i:i+length]
                    if not current_word.strip():  # 跳过空白字符
                        continue
                    
                    # 先检查是否是原词
                    if current_word in self.original_words_map:
                        target = self.original_words_map[current_word]
                        if current_word != target:  # 只在实际发生纠正时记录日志
                            logger.info(f"纠正: {current_word} -> {target}")
                        corrected_words.append(target)
                        i += length
                        matched = True
                        break
                    
                    # 如果不是原词，尝试相似度匹配
                    match_result = self.find_best_match(current_word, text)
                    if match_result:
                        best_match, similarity, threshold = match_result
                        # 获取目标词的上下文要求
                        target_context_words = self.target_words[best_match][1]
                        
                        # 如果有上下文要求，必须满足上下文条件；如果没有上下文要求，只检查相似度
                        if (not target_context_words or any(w in text for w in target_context_words)) and similarity >= threshold and current_word != best_match:
                            logger.info(f"纠正: {current_word} -> {best_match}")
                            corrected_words.append(best_match)
                            i += length
                            matched = True
                            break
                
                # 如果没有找到任何匹配，保持原字符
                if not matched:
                    corrected_words.append(text[i])
                    i += 1
            
            result = ''.join(corrected_words)
            if result != text:  # 只在最终结果有变化时记录日志
                logger.info(f"最终纠正: {text} -> {result}")
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
            # 纠正整体文本
            if "text" in recognition_result[0]:
                recognition_result[0]["text"] = self.correct_text(recognition_result[0]["text"])
            
            # 纠正每个句子片段
            if "sentence_info" in recognition_result[0]:
                for segment in recognition_result[0]["sentence_info"]:
                    if "sentence" in segment:
                        segment["sentence"] = self.correct_text(segment["sentence"])
            
            return recognition_result
            
        except Exception as e:
            logger.error(f"纠正识别结果失败: {str(e)}")
            return recognition_result

# 创建全局实例
text_corrector = TextCorrector()
