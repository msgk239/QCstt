"""
词库去重脚本
功能：根据冒号前面的词去重,保留第一次出现的映射关系
- 输入文件每行格式: word1：word2 或 word1:word2
- 以冒号前面的word1作为唯一键
- 重复的word1只保留第一次出现时对应的word2
- 输出统一使用中文冒号"："
"""
import os
def process_file(input_path, output_path):
    # 使用字典来存储唯一的映射关系
    unique_mappings = {}
    
    # 读取文件
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 处理每一行
    for line in lines:
        line = line.strip()
        # 同时处理英文冒号和中文冒号
        if not line or (':' not in line and '：' not in line):
            continue
            
        # 先尝试用英文冒号分割，如果失败则用中文冒号
        if ':' in line:
            left, right = line.split(':', 1)
        else:
            left, right = line.split('：', 1)
            
        left = left.strip()
        right = right.strip()
        
        # 存储到字典中，如果已存在则跳过
        if left not in unique_mappings:
            unique_mappings[left] = right
    
    # 写入新文件，统一使用中文冒号输出
    with open(output_path, 'w', encoding='utf-8') as f:
        for left, right in unique_mappings.items():
            f.write(f"{left}：{right}\n")

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 执行处理
input_file = os.path.join(script_dir, "原始词库.txt")
output_file = os.path.join(script_dir, "原始词库_去重.txt")
process_file(input_file, output_file) 