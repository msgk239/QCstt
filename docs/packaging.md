# 打包说明

## 1. 环境准备
```bash
# 确保在正确的conda环境
conda activate your_env
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
```bash
# 执行打包命令(使用当前conda环境)
python -m nuitka \
    --windows-standalone-gui \
    --output-dir=Y2W \
    --include-data-dir=frontend/dist=Y2W/frontend/dist \
    --include-data-dir=server=Y2W/server \
    --include-data-dir=.cache=Y2W/.cache \
    --follow-imports \
    --include-package=funasr \
    --include-package=torch \
    --include-package=fastapi \
    server/api/app.py
```

## 4. 注意事项
- 确保在正确的conda环境
- 所有文件会在 Y2W 目录下
- 数据文件(如热词)可以正常读写
