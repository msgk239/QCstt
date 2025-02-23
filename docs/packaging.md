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
python -m nuitka `
--standalone `
--windows-disable-console `
--output-dir=QCstt `
--include-data-dir="frontend/dist=frontend/dist" `
--include-data-dir="server=server" `
--include-data-dir=".cache=.cache" `
--nofollow-import-to=*.tests `
--windows-icon-from-ico="frontend/dist/favicon.ico" `
--mingw64 `
--jobs=4 `
--lto=yes `
--noinclude-pytest-mode=nofollow `
--noinclude-setuptools-mode=nofollow `
--report=QCstt_report.xml `
--python-flag=no_site `
--python-flag=no_warnings `
--python-flag=no_asserts `
"server/api/QCstt.py"
```

### 3.2 生产环境测试打包（有控制台）
```powershell
python -m nuitka `
--standalone `
--output-dir=QCstt_test `
--include-data-dir="frontend/dist=frontend/dist" `
--include-data-dir="server=server" `
--include-data-dir=".cache=.cache" `
--nofollow-import-to=*.tests `
--windows-icon-from-ico="frontend/dist/favicon.ico" `
--module-parameter=torch-disable-jit=no `
--module-parameter=numba-disable-jit=no `
--mingw64 `
--jobs=6 `
--lto=yes `
--noinclude-pytest-mode=nofollow `
--noinclude-setuptools-mode=nofollow `
--report=QCstt_test_report.xml `
--python-flag=no_site `
"server/api/QCstt.py"
```

### 3.3 打包参数说明
- `--standalone`: 生成独立可执行程序
- `--windows-disable-console`: 禁用控制台窗口
- `--output-dir`: 指定输出目录
- `--include-data-dir`: 包含需要的数据文件和目录
- `--nofollow-import-to`: 排除测试文件
- `--windows-icon-from-ico`: 设置程序图标
- `--mingw64`: 使用MinGW64编译器(性能最好,约20%性能提升)
- `--jobs`: 自动设置并行编译数
- `--lto`: 启用链接时优化
- `--noinclude-pytest-mode`: 排除测试相关依赖
- `--noinclude-setuptools-mode`: 排除安装相关依赖
- `--report`: 生成编译报告
- `--python-flag`: 设置Python运行时标志
- `--module-parameter`: 控制特定模块的行为

## 4. 注意事项
- 确保在正确的conda环境
- QCstt 目录为生产环境版本（无控制台）
- QCstt_test 目录为测试版本（有控制台，可查看日志）
- 数据文件(如热词)可以正常读写
- 确保 frontend/dist/favicon.ico 图标文件存在
- 首次编译时如果提示下载 ccache.exe，建议选择yes以启用编译缓存
- 如果内存不足,可以添加 --low-memory 选项
- 编译报告可以帮助分析和优化依赖
- 可以通过环境变量 NUITKA_CACHE_DIR 自定义缓存目录位置
- 如果遇到资源访问错误,检查 Windows Defender 是否在扫描

### 4.1 其他可用的编译选项
- `--onefile`: 生成单个可执行文件，方便分发程序
- `--include-package-data`: 自动检测和包含包的数据文件，避免手动指定
- `--disable-console`: GUI程序可用此选项隐藏控制台窗口
- `--macos-create-app-bundle`: 在macOS上创建标准的.app应用包
- `--macos-app-icon=app.icns`: 设置macOS应用图标
- `--linux-icon=app.png`: 设置Linux应用图标
- `--low-memory`: 减少编译时内存使用，适用于内存受限环境

## 5. 重新编译说明

### 5.1 前端文件更新
如果只修改了前端文件（frontend/dist 目录下的文件），不需要重新编译：
```
# 直接复制新的前端文件到打包目录
xcopy /E /Y frontend\dist\* QCstt_test\frontend\dist\
# 或者生产环境
xcopy /E /Y frontend\dist\* QCstt\frontend\dist\
```

### 5.2 后端代码更新
如果修改了后端代码（server/api 目录下的文件），需要重新编译。编译会自动使用缓存加快速度。

### 5.3 编译优化说明
- MinGW64 编译器比 MSVC 性能提升约20%,是推荐的编译器选择
- 不建议使用 MSVC 的 clang-cl,虽然比 MSVC 快但比 MinGW64 慢且配置复杂
- 编译缓存默认启用,存储在用户目录下
- --jobs 选项会根据CPU核心数自动优化并行编译
- anti-bloat 插件可以优化依赖包含
- 编译报告可以帮助分析优化空间
- 如果编译出现问题,可以逐步去掉优化选项进行测试
- 静态链接 Python 库可以避免 DLL 调用带来的性能损失
- Windows Defender 和索引服务可能会影响编译,建议临时关闭
- 使用 python -m nuitka 而不是直接运行 nuitka 命令
- python-flag 选项可以优化运行时性能
- 可以通过 CCFLAGS 和 LDFLAGS 环境变量传递额外的编译选项

### 5.4 运行时依赖说明
- Windows 10 及以上系统自带 ucrt.dll
- 使用 MinGW64 时需要 Visual C Runtime 2015
- 编译后可以删除 dist 目录中的 api-ms-crt-*.dll 文件
- 运行时检测编译状态可以使用 __compiled__ 属性
