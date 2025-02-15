import os
from typing import Dict, List, Tuple
import re

def is_pure_english(text: str) -> bool:
    """检查是否为纯英文（包含空格和标点）"""
    # 移除空格和标点后检查是否只包含英文字母
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

def read_keywords_file() -> Dict[str, Tuple[float, List[str]]]:
    """读取keywords文件，返回 {目标词: (阈值, [原词列表])} 的字典"""
    keywords_dict = {}
    with open('keywords', 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split(maxsplit=2)
            target_word = parts[0]
            threshold = None
            original_words = []
            
            if len(parts) >= 2:
                # 检查第二部分是否为阈值
                if any(c.isdigit() for c in parts[1]):
                    try:
                        threshold = float(parts[1])
                        # 如果有第三部分，那就是原词列表
                        if len(parts) == 3:
                            original_words = [w.strip() for w in parts[2].split(',')]
                    except ValueError:
                        original_words = [w.strip() for w in line[len(target_word):].strip().split(',')]
                else:
                    original_words = [w.strip() for w in line[len(target_word):].strip().split(',')]
            
            # 处理原词列表：去除空格，过滤纯英文
            original_words = [process_original_word(w) for w in original_words if not is_pure_english(w)]
            keywords_dict[target_word] = (threshold, original_words)
    
    return keywords_dict

def read_word_mapping() -> Dict[str, str]:
    """读取词库.txt文件，返回 {原词: 目标词} 的字典"""
    mapping = {}
    with open('词库.txt', 'r', encoding='utf-8') as f:
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
    
    return mapping

def update_keywords_file(keywords_dict: Dict[str, Tuple[float, List[str]]], 
                        word_mapping: Dict[str, str]):
    """更新keywords文件"""
    # 收集所有目标词
    all_targets = set(keywords_dict.keys())
    all_targets.update(set(word_mapping.values()))
    
    # 为新目标词创建条目
    for target in word_mapping.values():
        if target not in keywords_dict:
            keywords_dict[target] = (None, [])
            print(f"添加新目标词：{target}")
    
    # 根据映射更新keywords_dict中的原词列表
    for original, target in word_mapping.items():
        threshold, original_words = keywords_dict[target]
        # 处理原词：去除空格
        processed_original = process_original_word(original)
        if processed_original not in original_words:
            original_words.append(processed_original)
            keywords_dict[target] = (threshold, original_words)
    
    # 写入更新后的keywords文件
    with open('keywords', 'w', encoding='utf-8') as f:
        # 使用自定义排序规则
        sorted_items = sorted(keywords_dict.items(), key=lambda x: get_sort_key(x[0]))
        for target_word, (threshold, original_words) in sorted_items:
            line = target_word
            if threshold is not None:
                line += f" {threshold}"
            if original_words:
                line += f" {','.join(original_words)}"
            f.write(line + '\n')

def main():
    # 读取现有的keywords文件
    print("读取keywords文件...")
    keywords_dict = read_keywords_file()
    
    # 读取词库映射
    print("读取词库.txt文件...")
    word_mapping = read_word_mapping()
    
    # 更新keywords文件
    print("更新keywords文件...")
    update_keywords_file(keywords_dict, word_mapping)
    
    print("完成！")

if __name__ == "__main__":
    main() 