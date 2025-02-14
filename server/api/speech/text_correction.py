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
        # 存储格式: {word: (pinyin_list, context_words, threshold)}
        self.target_words: Dict[str, Tuple[List[str], List[str], float]] = {}
        self.pinyin_cache = {}  # 缓存词语的拼音结果
        self.load_config()

    def load_config(self) -> None:
        """从txt文件更新yaml配置文件，并加载配置"""
        try:
            # 添加自定义的YAML表示方法
            def represent_list(dumper, data):
                return dumper.represent_sequence('tag:yaml.org,2002:seq', data, flow_style=True)
            yaml.add_representer(list, represent_list)
            
            keywords_file = os.path.join(self.base_dir, "keywords")
            keywords = []
            thresholds = {}  # 存储单独设置的阈值
            
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        # 检查是否有阈值设置
                        parts = line.split()
                        # 检查第二部分是否是数字（支持各种小数格式）
                        if len(parts) == 2 and any(c.isdigit() for c in parts[1]):
                            try:
                                word = parts[0]
                                threshold = float(parts[1])
                                keywords.append(word)
                                thresholds[word] = threshold
                                logger.info(f"词 '{word}' 设置阈值: {threshold}")
                            except ValueError:
                                # 如果转换失败，就当作普通词处理
                                keywords.append(line)
                        else:
                            keywords.append(line)
            
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
                    # 使用单独设置的阈值或默认阈值
                    threshold = thresholds.get(word, 0.6)
                    config['target_words'][word] = {
                        'pinyin': self.word_to_pinyin(word),
                        'context_words': [],
                        'similarity_threshold': threshold
                    }
                else:
                    # 保留已有词的配置，但更新阈值
                    config['target_words'][word] = existing_config['target_words'][word]
                    if word in thresholds:
                        config['target_words'][word]['similarity_threshold'] = thresholds[word]
                    else:
                        config['target_words'][word]['similarity_threshold'] = 0.6
            
            # 保存更新后的配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
            
            # 加载配置到内存
            for word, info in config['target_words'].items():
                pinyin_list = info.get('pinyin', [])
                context_words = info.get('context_words', [])
                threshold = info.get('similarity_threshold', 0.6)
                self.target_words[word] = (pinyin_list, context_words, threshold)
                
            logger.info(f"成功加载 {len(self.target_words)} 个目标词配置")
            
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

    def find_best_match(self, word: str, context: str = "") -> Optional[str]:
        """找到最匹配的目标关键词"""
        word_pinyin = self.word_to_pinyin(word)
        best_match = None
        highest_similarity = 0
        
        logger.info(f"正在匹配词: {word} (拼音: {word_pinyin})")
        
        for target_word, (target_pinyin, context_words, threshold) in self.target_words.items():
            # 检查词长是否相同
            if len(word) != len(target_word):
                continue
                
            # 计算拼音相似度
            similarity = self.calculate_pinyin_similarity(word_pinyin, target_pinyin)
            
            # 添加详细的调试信息
            logger.info(f"对比: {word}({word_pinyin}) vs {target_word}({target_pinyin}), "
                       f"相似度: {similarity:.2f}, 阈值: {threshold}")
            
            # 如果有上下文词，提高相似度要求
            if context_words and not any(w in context for w in context_words):
                threshold += 0.1
                
            if similarity > highest_similarity and similarity >= threshold:
                highest_similarity = similarity
                best_match = target_word
        
        if best_match:
            logger.info(f"找到最佳匹配: {best_match}, 相似度: {highest_similarity:.2f}")
        else:
            logger.info("未找到匹配")
        
        return best_match

    def correct_text(self, text: str) -> str:
        """纠正文本中的词语
        
        Args:
            text: 待纠正的文本
            
        Returns:
            纠正后的文本
        """
        if not self.target_words:
            return text
            
        try:
            # 先尝试完整匹配
            best_match = self.find_best_match(text)
            if best_match:
                logger.info(f"词语纠正: {text} -> {best_match}")
                return best_match
            
            # 如果完整匹配失败，且长度与任何目标词不同，直接返回原文本
            if not any(len(text) == len(target) for target in self.target_words.keys()):
                return text
            
            # 分词并纠正
            words = list(text)
            corrected_words = []
            
            i = 0
            while i < len(words):
                # 尝试目标词长度的匹配
                matched = False
                target_lengths = set(len(target) for target in self.target_words.keys())
                
                for length in sorted(target_lengths, reverse=True):
                    if i + length > len(words):
                        continue
                        
                    current_word = ''.join(words[i:i+length])
                    best_match = self.find_best_match(current_word)
                    
                    if best_match:
                        corrected_words.append(best_match)
                        i += length
                        matched = True
                        logger.info(f"词语纠正: {current_word} -> {best_match}")
                        break
                
                if not matched:
                    corrected_words.append(words[i])
                    i += 1
            
            return ''.join(corrected_words)
            
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
