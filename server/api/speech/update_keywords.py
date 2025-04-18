import os
from typing import Dict, List, Tuple, Set
import re
from ..logger import get_logger

logger = get_logger(__name__)

def is_pure_english(text: str) -> bool:
    """检查是否为纯英文（包含空格和标点）"""
    cleaned_text = re.sub(r'[^a-zA-Z]', '', text)
    return bool(cleaned_text) and all(c.isascii() and c.isalpha() for c in cleaned_text)

def process_original_word(word: str) -> str:
    """处理原词：去除空格"""
    return word.replace(' ', '')

def get_sort_key(word):
    """获取排序键值
    
    排序规则：
    1. 英文字母开头的词
    2. "第X灵"格式的词
    3. 纯中文数字开头的"X灵"
    4. 特殊前缀词
    5. 其他词
    """
    # 中文数字映射
    cn_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
        '零': '0'
    }
    
    # 1. 处理英文字母开头的词
    if any(c.isascii() and c.isalpha() for c in word):
        return f"A_{word}"
    
    # 2. 处理"第X灵"的情况
    if word.startswith('第') and '灵' in word:
        second_char = word[1]
        # 2.1 处理阿拉伯数字的情况
        if second_char.isdigit():
            num = second_char
            return f"B_{num.zfill(2)}"
        # 2.2 处理中文数字的情况
        if second_char in cn_numbers:
            num = cn_numbers[second_char]
            return f"B_{num.zfill(2)}"
    
    # 3. 处理纯中文数字开头的"X灵"
    if word[0] in cn_numbers and '灵' in word:
        num = cn_numbers[word[0]]
        return f"C_{num.zfill(2)}"
    
    # 4. 处理特殊前缀词
    special_prefixes = ['主', '外', '体', '肉体', '复合', '集体']
    for i, prefix in enumerate(special_prefixes):
        if word.startswith(prefix):
            return f"D_{i:02d}_{word}"
    
    # 5. 其他词按原始顺序排序
    return f"E_{word}"

def merge_configs(configs: List[Tuple[int, float, List[str], List[str], str]]) -> Tuple[float, List[str], List[str]]:
    """合并配置
    
    Args:
        configs: [(行号, 阈值, 原词列表, 上下文词列表, 原始行)]
    Returns:
        (合并后阈值, 合并后原词列表, 合并后上下文词列表)
    """
    # 收集所有非None的阈值
    thresholds = [t for _, t, _, _, _ in configs if t is not None]
    # 合并所有原词列表
    all_original_words = set()
    # 合并所有上下文词
    all_context_words = set()
    
    for _, _, orig_words, context_words, _ in configs:
        all_original_words.update(orig_words)
        all_context_words.update(context_words)
        
    # 使用最严格的阈值
    final_threshold = max(thresholds) if thresholds else 0.9
    return (final_threshold, list(all_original_words), list(all_context_words))

def filter_special_chars(text: str) -> str:
    """只保留中文、英文字母和数字"""
    return ''.join(char for char in text 
                  if ('\u4e00' <= char <= '\u9fff' or  # 中文字符
                      'a' <= char.lower() <= 'z' or    # 英文字母
                      '0' <= char <= '9'))             # 数字

def is_valid_target(text: str) -> bool:
    """检查目标词是否合法（不能只有一个中文字）"""
    # 过滤掉特殊字符
    filtered_text = filter_special_chars(text)
    if not filtered_text:
        return False
        
    # 统计中文字符数
    chinese_chars = len([c for c in filtered_text if '\u4e00' <= c <= '\u9fff'])
    
    # 如果只有一个中文字且没有其他字符，则不合法
    if chinese_chars == 1 and len(filtered_text) == 1:
        return False
        
    return True

def read_keywords_file(file_path='keywords') -> Dict[str, List[Tuple[int, float, List[str], List[str], str]]]:
    """读取keywords文件，返回 {目标词: [(行号, 阈值, 原词列表, 上下文词列表, 原始行)]} 的字典"""
    # 修改为使用当前文件所在目录的相对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.join(current_dir, file_path)
    
    keywords_dict = {}
    duplicate_words = {}
    
    with open(keywords_path, 'r', encoding='utf-8') as f:
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
            
            parts = line.split(maxsplit=2)
            if not parts:
                continue
                
            target_word = parts[0]
            
            # 检查目标词
            filtered_word = filter_special_chars(target_word)
            if not is_valid_target(target_word):
                if not filtered_word:
                    logger.warning(f"第 {line_number} 行: 目标词 '{target_word}' 过滤特殊字符后为空，已跳过")
                    continue
                elif len(filtered_word) == 1 and '\u4e00' <= filtered_word <= '\u9fff':
                    logger.warning(f"第 {line_number} 行: 目标词 '{target_word}' 只包含一个中文字 '{filtered_word}'，已跳过")
                    continue
            elif filtered_word != target_word:
                logger.warning(f"第 {line_number} 行: 目标词 '{target_word}' 包含特殊字符，已过滤为 '{filtered_word}'")
                target_word = filtered_word
            
            threshold = None
            original_words = []
            
            if len(parts) >= 2:
                # 检查第二部分是否为阈值
                if any(c.isdigit() for c in parts[1]):
                    try:
                        threshold = float(parts[1])
                        # 如果有第三部分，那就是原词列表
                        if len(parts) == 3:
                            original_words = [w.strip() for w in parts[2].replace('，', ',').split(',')]
                    except ValueError:
                        original_words = [w.strip() for w in line[len(target_word):].strip().replace('，', ',').split(',')]
                else:
                    original_words = [w.strip() for w in line[len(target_word):].strip().replace('，', ',').split(',')]
            
            # 处理原词列表：去除空格，过滤纯英文
            original_words = [process_original_word(w) for w in original_words if not is_pure_english(w)]
            
            # 记录配置
            if target_word not in keywords_dict:
                keywords_dict[target_word] = []
            keywords_dict[target_word].append((line_number, threshold, original_words, context_list, line))
            
            # 检查是否重复
            if len(keywords_dict[target_word]) > 1:
                duplicate_words[target_word] = keywords_dict[target_word]
    
    # 输出重复词条警告
    if duplicate_words:
        logger.warning("\n发现重复的目标词配置：")
        for word, occurrences in duplicate_words.items():
            logger.warning(f"\n目标词 '{word}' 在以下行出现多次：")
            for line_num, _, _, _, line in occurrences:
                logger.warning(f"第 {line_num} 行: {line}")
            # 显示合并结果
            threshold, orig_words, context_words = merge_configs(occurrences)
            logger.info(f"已自动合并配置：")
            logger.info(f"- 使用最大阈值: {threshold}")
            logger.info(f"- 合并后的原词数量: {len(orig_words)}")
            logger.info(f"- 合并后的上下文词数量: {len(context_words)}")
    
    return keywords_dict

def read_word_mapping() -> Dict[str, str]:
    """读取词库文件，返回 {原词: 目标词} 的字典"""
    mapping = {}
    # 修改为使用当前文件所在目录的相对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, 'ciku', '原始词库_去重.txt')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '：' not in line:
                    continue
                
                original, target = line.split('：', 1)
                original = original.strip()
                target = target.strip()
                
                # 跳过纯英文原词
                if is_pure_english(original):
                    continue
                    
                # 处理原词：去除空格
                original = process_original_word(original)
                mapping[original] = target
        
        logger.info(f"从{file_path}读取了 {len(mapping)} 个映射关系")
    except FileNotFoundError:
        logger.warning(f"{file_path}文件不存在")
    except Exception as e:
        logger.error(f"读取{file_path}时出错: {str(e)}")
    
    return mapping

def update_keywords_file(keywords_dict: Dict[str, List[Tuple[int, float, List[str], List[str], str]]], 
                        word_mapping: Dict[str, str]):
    """更新keywords文件"""
    # 修改为使用当前文件所在目录的相对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    keywords_path = os.path.join(current_dir, 'keywords')
    
    # 首先读取原文件，保存所有注释行
    comments = []
    with open(keywords_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('#'):
                comments.append(line)
    
    # 收集所有目标词，并过滤不合法的目标词
    all_targets = {filter_special_chars(word) for word in keywords_dict.keys() 
                  if is_valid_target(word)}
    all_targets.update({filter_special_chars(word) for word in word_mapping.values() 
                       if is_valid_target(word)})
    
    # 合并配置
    final_configs = {}
    
    # 首先处理已有的配置
    for word, configs in keywords_dict.items():
        if not is_valid_target(word):
            logger.warning(f"跳过不合法的目标词：{word}")
            continue
        if len(configs) > 1:
            # 有重复配置，需要合并
            final_configs[word] = merge_configs(configs)
        else:
            # 单个配置，直接使用
            _, threshold, orig_words, context_words, _ = configs[0]
            final_configs[word] = (threshold, orig_words, context_words)
    
    # 处理词库映射中的新目标词
    for target in word_mapping.values():
        filtered_target = filter_special_chars(target)
        if not is_valid_target(target):
            if not filtered_target:
                logger.warning(f"跳过目标词 '{target}'：过滤特殊字符后为空")
                continue
            elif len(filtered_target) == 1 and '\u4e00' <= filtered_target <= '\u9fff':
                logger.warning(f"跳过目标词 '{target}'：只包含一个中文字 '{filtered_target}'")
                continue
        elif filtered_target != target:
            logger.warning(f"目标词 '{target}' 包含特殊字符，已过滤为 '{filtered_target}'")
            target = filtered_target
        
        if target not in final_configs:
            final_configs[target] = (None, [], [])
            logger.info(f"添加新目标词：{target}")
    
    # 根据映射更新原词列表
    for original, target in word_mapping.items():
        # 过滤目标词中的特殊字符
        filtered_target = filter_special_chars(target)
        if filtered_target != target:
            logger.warning(f"目标词 '{target}' 包含特殊字符，已过滤为 '{filtered_target}'")
            target = filtered_target
            
        # 如果目标词不在配置中，跳过并提示
        if target not in final_configs:
            logger.warning(f"跳过映射 '{original} -> {target}'：目标词不在配置列表中")
            continue
            
        threshold, original_words, context_words = final_configs[target]
        processed_original = process_original_word(original)
        if processed_original not in original_words:
            original_words.append(processed_original)
            final_configs[target] = (threshold, original_words, context_words)
    
    # 写入更新后的keywords文件
    with open(keywords_path, 'w', encoding='utf-8') as f:
        # 首先写入所有注释
        for comment in comments:
            f.write(comment)
            
        # 如果最后一个注释后面没有空行，添加一个空行
        if comments and not comments[-1].strip() == '':
            f.write('\n')
            
        # 使用自定义排序规则写入更新的内容
        sorted_items = sorted(final_configs.items(), key=lambda x: get_sort_key(x[0]))
        for target_word, (threshold, original_words, context_words) in sorted_items:
            line = target_word
            if threshold is not None:
                line += f" {threshold}"
            if original_words:
                line += f" {','.join(original_words)}"
            if context_words:
                line += f" ({','.join(context_words)})"
            f.write(line + '\n')
    
    logger.info(f"更新完成，共处理 {len(final_configs)} 个目标词")

def main():
    logger.info("开始更新keywords文件...")
    
    # 读取现有的keywords文件
    logger.debug("读取keywords文件...")
    keywords_dict = read_keywords_file()
    
    # 读取词库映射
    logger.debug("读取词库文件...")
    word_mapping = read_word_mapping()
    
    # 更新keywords文件
    logger.info("更新keywords文件...")
    update_keywords_file(keywords_dict, word_mapping)
    
    logger.info("全部完成！")

__all__ = [
    'read_keywords_file',
    'get_sort_key',
    'merge_configs',
    'process_original_word',
    'is_pure_english',
    'read_word_mapping',
    'update_keywords_file'
]

if __name__ == "__main__":
    main() 