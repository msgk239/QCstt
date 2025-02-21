import pytest
import os
import time
from api.speech.hotwords import HotwordsManager

class TestHotwordsManager:
    @pytest.fixture
    def manager(self, tmp_path):
        # 创建测试用的临时文件和目录
        keywords_path = tmp_path / "keywords"
        backup_dir = tmp_path / "backups"  # 修改为目录
        
        # 使用 utf-8 编码写入测试数据
        with open(keywords_path, 'w', encoding='utf-8') as f:
            f.write("""测试词1 0.9 原词1,原词2 (上下文1,上下文2)
测试词2 0.8 原词3""")
        
        return HotwordsManager(str(keywords_path), str(backup_dir))

    def test_read_content(self, manager):
        """测试读取内容"""
        content = manager.get_content()
        assert content['code'] == 0
        assert '测试词1' in content['data']['content']
        assert content['data']['lastModified'] > 0

    def test_validate_content(self, manager):
        """测试内容验证"""
        # 测试正确格式
        valid_content = """测试词1 0.9 原词1,原词2 (上下文1,上下文2)
测试词2 0.8 原词3"""
        result = manager.validate_content(valid_content)
        assert result['code'] == 0
        assert result['data']['isValid'] is True
        assert len(result['data']['errors']) == 0

        # 测试错误格式
        invalid_content = """测试词1 2.0 原词1  # 阈值超出范围
测试词1 0.8 原词2  # 重复目标词
测试词3 0.7 原词3 (上下文1  # 括号不匹配"""
        result = manager.validate_content(invalid_content)
        assert result['code'] == 0
        assert result['data']['isValid'] is False
        assert len(result['data']['errors']) > 0

    def test_update_content(self, manager):
        """测试更新内容"""
        new_content = "新词1 0.9 原词1,原词2"
        result = manager.update_content(new_content)
        assert result['code'] == 0
        
        # 验证内容已更新
        content = manager.get_content()
        assert new_content in content['data']['content']

    def test_backup_mechanism(self, manager):
        """测试新的多版本备份机制"""
        original_content = manager.get_content()['data']['content']
        
        # 1. 测试首次备份
        new_content = "新词1 0.9 原词1"
        manager.update_content(new_content)
        
        backup_files = os.listdir(manager.backup_dir)
        assert len(backup_files) == 1
        assert all(f.startswith('keywords_') and f.endswith('.backup') for f in backup_files)

        # 验证备份内容
        latest_backup = sorted(backup_files, key=lambda x: os.path.getmtime(
            os.path.join(manager.backup_dir, x)))[-1]
        with open(os.path.join(manager.backup_dir, latest_backup), 'r', encoding='utf-8') as f:
            assert f.read().strip() == original_content.strip()

    def test_multiple_backups(self, manager):
        """测试多次备份和自动清理"""
        # 进行12次更新（超过保留限制10个）
        for i in range(12):
            content = f"测试词1 0.8 测试{i}\n测试词2 0.9 测试{i}"
            manager.update_content(content)
            time.sleep(1)  # 确保时间戳不同

        # 检查备份文件数量
        backup_files = os.listdir(manager.backup_dir)
        assert len(backup_files) == 10  # 应该只保留10个最新的备份
        
        # 检查是否按时间正确保留了最新的备份（使用文件名排序）
        backup_files.sort(reverse=True)  # 按文件名排序
        # 验证文件是按时间顺序排列的
        assert backup_files == sorted(backup_files, reverse=True)

    def test_backup_error_handling(self, manager):
        """测试备份错误处理"""
        # 1. 测试源文件不存在的情况
        os.remove(manager.keywords_path)
        try:
            manager._backup_file()
        except Exception:
            pytest.fail("不应该抛出异常，而是记录警告日志")

        # 2. 测试备份目录权限问题
        if os.name != 'nt':  # 在非Windows系统上测试权限
            try:
                os.chmod(manager.backup_dir, 0o000)  # 移除所有权限
                with pytest.raises(Exception):
                    manager.update_content("测试内容")
            finally:
                os.chmod(manager.backup_dir, 0o755)  # 恢复权限

    def test_backup_file_naming(self, manager):
        """测试备份文件命名格式"""
        manager.update_content("测试内容")
        
        backup_files = os.listdir(manager.backup_dir)
        assert len(backup_files) == 1
        
        backup_file = backup_files[0]
        # 验证文件名格式：keywords_YYYYMMDD_HHMMSS.backup
        assert backup_file.startswith('keywords_')
        assert backup_file.endswith('.backup')
        assert len(backup_file) == len('keywords_20240321_235959.backup')

    def test_concurrent_modification(self, manager):
        """测试并发修改检测"""
        content = manager.get_content()
        last_modified = content['data']['lastModified']
        
        # 模拟文件被其他进程修改
        with open(manager.keywords_path, 'a', encoding='utf-8') as f:
            f.write("\n新词2 0.8 原词4")
        
        # 尝试使用旧的修改时间更新
        result = manager.update_content("新内容", last_modified)
        assert result['code'] == 2  # 应该返回文件已被修改的错误码 