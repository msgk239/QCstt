def extract_keywords(input_file, output_file):
    # 用于存储提取的关键词
    keywords = set()
    
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '：' in line:  # 使用中文冒号
                # 提取冒号后的内容
                keyword = line.split('：')[1].strip()
                keywords.add(keyword)
    
    # 将结果写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for keyword in sorted(keywords):  # 排序后写入
            f.write(keyword + '\n')

if __name__ == '__main__':
    input_file = '词库.txt'
    output_file = 'keywords.txt'
    extract_keywords(input_file, output_file)
    print('关键词提取完成，已保存到', output_file) 