def get_sort_key(word):
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
    
    # 5. 其他词按拼音排序
    return f"E_{word}"

def deduplicate_keywords(input_file, output_file):
    print(f"开始处理文件: {input_file}")  # 调试信息
    # 用于存储关键词，key是比较用的部分（空格前），value是完整的行
    keywords_dict = {}
    # 用于记录被去重的项
    duplicates = []
    
    # 读取输入文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            print(f"读取到 {len(lines)} 行数据")  # 调试信息
            
            for line in lines:
                line = line.strip()
                if not line:  # 跳过空行
                    continue
                    
                # 用空格分割，取第一部分作为比较key
                compare_key = line.split(' ')[0]
                
                # 如果这个key已经存在，说明是重复项
                if compare_key in keywords_dict:
                    duplicates.append(f"去掉重复项: {line} (与已存在的 {keywords_dict[compare_key]} 重复)")
                else:
                    keywords_dict[compare_key] = line
        
        print(f"处理后得到 {len(keywords_dict)} 个唯一项")  # 调试信息
        
        # 将结果写入输出文件
        with open(output_file, 'w', encoding='utf-8') as f:
            # 使用自定义排序规则
            sorted_keywords = sorted(keywords_dict.values(), key=lambda x: get_sort_key(x.split(' ')[0]))
            for keyword in sorted_keywords:
                f.write(keyword + '\n')
        
        # 输出处理日志
        print("\n处理完成！")
        print(f"总共去掉了 {len(duplicates)} 个重复项")
        if duplicates:
            print("\n去重详情：")
            for dup in duplicates:
                print(dup)
        print(f"\n结果已保存到: {output_file}")
        return True
    except Exception as e:
        print(f"处理过程中出现错误: {str(e)}")
        return False

if __name__ == '__main__':
    import sys
    input_file = 'keywords'
    output_file = 'keywords_unique.txt'
    print("脚本开始执行...")  # 调试信息
    success = deduplicate_keywords(input_file, output_file)
    print(f"脚本执行{'成功' if success else '失败'}")  # 调试信息
    sys.stdout.flush() 