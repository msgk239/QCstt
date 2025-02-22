"""
处理原始词库映射关系的脚本

功能：
1. 读取原始词库_去重.txt中的词语映射关系
2. 对原词进行处理（去除空格，过滤纯英文词）
3. 将相同目标词的原词归类在一起
4. 生成处理后的映射文件（处理后词库.txt），格式为"目标词：原词1,原词2,..."

使用方法：
1. 确保原始词库_去重.txt在同目录下
2. 运行脚本
3. 生成处理后词库.txt

注意：此脚本仅处理词库映射，不会修改keywords文件
"""

import os
from typing import Dict, List, Tuple
import re
from collections import defaultdict
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 获取当前脚本所在目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def is_pure_english(text: str) -> bool:
    """检查是否为纯英文（包含空格和标点）"""
    cleaned_text = re.sub(r'[^a-zA-Z]', '', text)
    return bool(cleaned_text) and all(c.isascii() and c.isalpha() for c in cleaned_text)

def process_original_word(word: str) -> str:
    """处理原词：去除空格"""
    return word.replace(' ', '')

def read_original_mapping() -> Dict[str, set]:
    """读取原始词库文件，返回 {目标词: {原词集合}} 的字典"""
    input_file = os.path.join(SCRIPT_DIR, '原始词库_去重.txt')
    mapping = defaultdict(set)
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
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
                mapping[target].add(original)
        
        logger.info(f"从原始词库文件读取了 {len(mapping)} 个目标词的映射关系")
    except FileNotFoundError:
        logger.error(f"文件 {input_file} 不存在")
    except Exception as e:
        logger.error(f"读取文件时出错: {str(e)}")
    
    return mapping

def write_processed_mapping(mapping: Dict[str, set]):
    """将处理后的映射写入新文件，格式为 目标词：原词1,原词2,..."""
    output_file = os.path.join(SCRIPT_DIR, '处理后词库.txt')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for target, originals in sorted(mapping.items()):
                sorted_originals = sorted(originals)
                f.write(f"{target}：{','.join(sorted_originals)}\n")
        logger.info(f"已将处理后的 {len(mapping)} 个目标词的映射关系写入 {output_file}")
    except Exception as e:
        logger.error(f"写入文件时出错: {str(e)}")

def main():
    logger.info("开始处理原始词库...")
    
    # 读取原始映射
    mapping = read_original_mapping()
    
    # 写入处理后的文件
    write_processed_mapping(mapping)
    
    logger.info("处理完成！")

if __name__ == "__main__":
    main() 