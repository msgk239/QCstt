# 打包说明

## 1. 环境准备
```bash
# 确保在正确的conda环境 (.conda)
conda activate d:\AI\y2w\.conda
pip install nuitka
```

## 2. 目录结构
```
Y2W/                 # 应用根目录
├── frontend/dist/    # 前端打包后的文件
├── server/           # 后端服务
└── .cache/           # 模型文件
    └── modelscope/hub/iic/
```

## 3. 打包命令

### 3.1 生产环境打包（无控制台）
```powershell
# PowerShell 多行格式
python -m nuitka `
    --standalone `
    --windows-disable-console `
    --output-dir=QCstt `
    --include-data-dir=frontend/dist=QCstt/frontend/dist `
    --include-data-dir=server=QCstt/server `
    --include-data-dir=.cache=QCstt/.cache `
    --follow-imports `
    --nofollow-import-to=*.tests `
    --windows-icon-from-ico=frontend/dist/favicon.ico `
    --include-package=funasr `
    --include-package=torch `
    --include-package=fastapi `
    server/api/package.py

# PowerShell 单行格式
python -m nuitka --standalone --windows-disable-console --output-dir=QCstt --include-data-dir=frontend/dist=QCstt/frontend/dist --include-data-dir=server=QCstt/server --include-data-dir=.cache=QCstt/.cache --follow-imports --nofollow-import-to=*.tests --windows-icon-from-ico=frontend/dist/favicon.ico --include-package=funasr --include-package=torch --include-package=fastapi server/api/package.py
```

### 3.2 生产环境测试打包（有控制台）
```powershell
# PowerShell 多行格式
python -m nuitka `
    --standalone `
    --output-dir=QCstt_test `
    --include-data-dir=frontend/dist=QCstt_test/frontend/dist `
    --include-data-dir=server=QCstt_test/server `
    --include-data-dir=.cache=QCstt_test/.cache `
    --follow-imports `
    --nofollow-import-to=*.tests `
    --windows-icon-from-ico=frontend/dist/favicon.ico `
    --include-package=funasr `
    --include-package=torch `
    --include-package=fastapi `
    server/api/prod.py

# PowerShell 单行格式
python -m nuitka --standalone --output-dir=QCstt_test --include-data-dir=frontend/dist=QCstt_test/frontend/dist --include-data-dir=server=QCstt_test/server --include-data-dir=.cache=QCstt_test/.cache --follow-imports --nofollow-import-to=*.tests --windows-icon-from-ico=frontend/dist/favicon.ico --include-package=funasr --include-package=torch --include-package=fastapi server/api/prod.py
```

## 4. 注意事项
- 确保在正确的conda环境
- QCstt 目录为生产环境版本（无控制台）
- QCstt_test 目录为测试版本（有控制台，可查看日志）
- 数据文件(如热词)可以正常读写
- 确保 frontend/dist/favicon.ico 图标文件存在
