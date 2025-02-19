import jieba
import pkuseg
import os
import importlib
import random
import time

# 首先从keywords文件生成词典
def create_dict_from_keywords(keywords_file, dict_file):
    """从keywords文件创建词典文件"""
    words = set()
    with open(keywords_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # 提取目标词（第一个空格前的部分）
                word = line.split()[0]
                if word:
                    words.add(word)
    
    # 写入词典文件
    with open(dict_file, 'w', encoding='utf-8') as f:
        for word in sorted(words):
            f.write(word + '\n')
    
    return words

# 生成词典文件
current_dir = os.path.dirname(os.path.abspath(__file__))
keywords_file = os.path.join(current_dir, 'keywords')
dict_file = os.path.join(current_dir, 'custom_dict.txt')
words = create_dict_from_keywords(keywords_file, dict_file)

# 可以选择固定测试集或随机测试集
USE_FIXED_TEST_SET = False  # 通过修改这个变量来切换模式

if USE_FIXED_TEST_SET:
    test_words = [
        "复合体灵", "主催一声", "互催", "潜催", "自催",
        "集体意识", "意识频谱", "意识窄化", "意识黏连", "意识漏洞",
        # ... 其他固定测试词 ...
    ]
else:
    test_words = random.sample(list(words), 30)

print("\n测试词列表：")
for i, word in enumerate(test_words, 1):
    print(f"{i}. {word}")

# 添加自定义词典
for word in test_words:
    jieba.add_word(word)    # 告诉jieba这些是完整的词

def count_uncut(results):
    return sum(1 for r in results if len(r.split(' | ')) == 1)

# 存储各分词工具的结果
all_results = {
    'jieba（带词典）': [],
    'jieba（原始）': [],
    'pkuseg（带词典）': [],
    'pkuseg（原始）': []
}

# jieba（原始）
print("\njieba分词结果（原始）：")
# 完全重新初始化jieba
importlib.reload(jieba)
jieba.setLogLevel(20)  # 设置日志级别，避免警告信息

for word in test_words:
    result = ' | '.join(jieba.cut(word))
    all_results['jieba（原始）'].append(result)
    print(f"{word}: {result}")

# jieba（带词典）
print("\njieba分词结果（带词典）：")
jieba.initialize()  # 重新初始化
jieba.setLogLevel(20)
# 先加载自定义词典中的词
for word in words:
    jieba.add_word(word)
# 再加载测试词列表
for word in test_words:
    jieba.add_word(word)
for word in test_words:
    result = ' | '.join(jieba.cut(word))
    all_results['jieba（带词典）'].append(result)
    print(f"{word}: {result}")

# pkuseg（原始）
print("\npkuseg分词结果（原始）：")
seg = pkuseg.pkuseg()
for word in test_words:
    result = ' | '.join(seg.cut(word))
    all_results['pkuseg（原始）'].append(result)
    print(f"{word}: {result}")

# pkuseg（带词典）
print("\npkuseg分词结果（带词典）：")
seg_with_dict = pkuseg.pkuseg(user_dict=dict_file)
for word in test_words:
    result = ' | '.join(seg_with_dict.cut(word))
    all_results['pkuseg（带词典）'].append(result)
    print(f"{word}: {result}")

# 统计和排名
print("\n统计结果：")
scores = {}
for tool, results in all_results.items():
    uncut_count = count_uncut(results)
    scores[tool] = uncut_count
    print(f"{tool}: 保持完整词数 {uncut_count}/30")

# 排名
print("\n最终排名：")
ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
for i, (tool, score) in enumerate(ranked, 1):
    print(f"{i}. {tool}: {score}/30分")

def test_init_time():
    print("\n=== 测试初始化时间 ===")
    
    # 测试jieba初始化时间
    start = time.time()
    jieba.initialize()
    jieba_time = time.time() - start
    print(f"jieba初始化时间: {jieba_time:.3f}秒")
    
    # 测试pkuseg初始化时间
    start = time.time()
    seg = pkuseg.pkuseg()
    pkuseg_time = time.time() - start
    print(f"pkuseg初始化时间: {pkuseg_time:.3f}秒")
    
    # 测试带词典的pkuseg初始化时间
    current_dir = os.path.dirname(os.path.abspath(__file__))
    dict_file = os.path.join(current_dir, 'custom_dict.txt')
    start = time.time()
    seg_with_dict = pkuseg.pkuseg(user_dict=dict_file)
    pkuseg_dict_time = time.time() - start
    print(f"pkuseg(带词典)初始化时间: {pkuseg_dict_time:.3f}秒")

def test_cut_speed():
    print("\n=== 测试分词速度 ===")
    
    # 准备测试数据
    test_texts = [
        # 短文本测试 (专业词汇)
        "".join(test_words),  
        # 长文本测试 (普通文本，约1万字)
        "这是一段比较长的测试文本，用来测试分词工具的性能。" * 500,
        # 混合文本测试 (约1万字，带专业词汇)
        f"这是一段混合了专业词汇的文本，{test_words[0]}和{test_words[1]}等。" * 250
    ]
    
    # 初始化分词器
    jieba.initialize()
    seg = pkuseg.pkuseg()
    seg_with_dict = pkuseg.pkuseg(user_dict=dict_file)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n测试文本{i} (长度: {len(text)}字)")
        
        # 每个分词器测试3次，取平均值
        for name, cut_func in [
            ("jieba原始分词", lambda t: list(jieba.cut(t))),
            ("jieba带词典分词", lambda t: list(jieba.cut(t))),
            ("pkuseg原始分词", lambda t: seg.cut(t)),
            ("pkuseg带词典分词", lambda t: seg_with_dict.cut(t))
        ]:
            times = []
            for _ in range(3):
                start = time.time()
                cut_func(text)
                times.append(time.time() - start)
            avg_time = sum(times) / len(times)
            print(f"{name}: {avg_time:.3f}秒 (最快: {min(times):.3f}秒, 最慢: {max(times):.3f}秒)")

def test_fenci():
    # 初始化分词器
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dict_path = os.path.join(base_dir, "custom_dict.txt")
    print(f"使用词典: {dict_path}")
    
    seg = pkuseg.pkuseg(model_name='news', user_dict=dict_path)
    
    # 测试用例
    test_cases = [
        "林体和零体都是灵体",
        "都是灵体",
        "这是灵体",
        "灵体很重要"
    ]
    
    for text in test_cases:
        words = seg.cut(text)
        print(f"\n原文: {text}")
        print(f"分词: {' | '.join(words)}")

if __name__ == "__main__":
    test_init_time()
    test_cut_speed()
    test_fenci()

"""
# 如果需要测试其他分词工具，请先安装相应的包：

# 安装 pkuseg:
# pip install pkuseg
"""
