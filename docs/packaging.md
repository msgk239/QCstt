# 打包说明
潜催语音转文字系统 (QianCui Speech-to-Text)

基于 FastAPI 和 Vue 3 开发的语音识别系统，支持多语言识别和多种音频格式。
本系统完全保护用户隐私，所有处理均在本地完成。
计划使用 nuitka 打包。
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
--plugin-enable=no-pil-jpeg `
"server/api/QCstt.py"
```

### 3.2 生产环境测试打包（有控制台，带调试选项）
```powershell
python -m nuitka `
--output-dir=QCstt `
--mingw64 `
--windows-icon-from-ico="frontend/dist/favicon.ico" `
--include-package=server `
--nofollow-import-to=*.tests `
--nofollow-import-to=pytest.* `
--noinclude-pytest-mode=nofollow `
--include-data-dir="frontend/dist=frontend/dist" `
--include-data-dir="server=server" `
--include-data-dir=".cache=.cache" `
"server/api/QCstt.py"

--noinclude-setuptools-mode=nofollow `
--python-flag=no_site `
--enable-plugin=no-qt `
--report=QCstt_deps_report.xml `
```
最后编译时4386
### 3.3 打包参数说明
- `--standalone`: 生成独立可执行程序
- `--windows-disable-console`: 禁用控制台窗口
- `--output-dir`: 指定输出目录
- `--include-data-dir`: 包含需要的数据文件和目录
- `--include-package`: 包含整个包及其所有模块
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
- `--debug`: 生成带有调试信息的可执行文件
- `--unstripped`: 保留调试信息，便于调试器交互
- `--trace-execution`: 跟踪程序执行流程
- `--experimental=debug-self-forking`: 调试自我分叉问题
- `--python-debug`: 使用Python的调试版本
- `--warn-implicit-exceptions`: 启用对编译时检测到的隐式异常的警告
- `--warn-unusual-code`: 启用对编译时检测到的异常代码的警告
- `--file-reference-choice=original`: 使用原始源文件位置作为`__file__`值
- `--verbose-output`: 输出详细的编译信息到指定文件

### 3.4 大型依赖库处理
### 排除编译的库
```powershell
# 以下库已确认不需要，可以安全排除编译
--nofollow-import-to=huggingface.* `
--nofollow-import-to=huggingface_hub.* `
--nofollow-import-to=gradio.* `
--nofollow-import-to=pytest.* `
```

### 减少torch模块数量
```powershell
# 以下torch子模块可以安全排除，减少模块数量
--nofollow-import-to=torch.vision `    # 图像处理相关，语音识别不需要
--nofollow-import-to=torch.distributed `  # 分布式训练相关，推理不需要
--nofollow-import-to=torch.optim `     # 优化器相关，推理不需要
```

注意：
1. 这些库已确认不用于核心功能，可以直接排除:
   - huggingface/huggingface_hub: 仅用于可选的模型下载
   - gradio: 仅用于演示界面
   - torch.vision: 图像处理相关，语音识别不需要
   - torch.distributed: 分布式训练相关，推理不需要
   - torch.optim: 优化器相关，推理不需要
2. 不需要复制这些库文件，因为:
   - 模型文件已预先下载到 .cache 目录
   - 模型加载使用 torch 等核心库
3. 如果后续发现有依赖问题，再重新评估

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

## 6. 调试技巧

### 6.1 调试选项说明
- `--debug` 和 `--unstripped` 选项会保留调试符号，使得可以使用调试器（如gdb、lldb或Visual Studio）进行调试
- `--trace-execution` 会在执行每行代码前输出该行代码，帮助跟踪程序执行流程
- `--python-debug` 使用Python的调试版本，可以捕获更多的内部错误
- `--file-reference-choice=original` 使`__file__`变量保持原始值，有助于解决路径问题
- `--warn-implicit-exceptions` 和 `--warn-unusual-code` 可以在编译时发现潜在问题

### 6.2 使用调试器运行
可以使用`--debugger`选项直接在调试器中运行编译后的程序：
```powershell
cd QCstt_test
# 使用自动选择的调试器
QCstt.exe --debugger

# 或者手动指定调试器（需要先设置环境变量）
$env:NUITKA_DEBUGGER_CHOICE = "gdb"  # 或 "lldb", "devenv" 等
QCstt.exe --debugger
```

### 6.3 分析段错误
对于段错误（Segmentation Fault）问题：
1. 使用带有所有调试选项的编译命令
2. 运行程序并记录崩溃时的堆栈跟踪
3. 检查`__file__`变量的值和路径计算是否正确
4. 使用环境变量启用详细日志：
   ```powershell
   $env:NUITKA_VERBOSITY = "debug"
   QCstt.exe
   ```

### 6.4 路径问题调试
对于`__file__`变量和路径问题：
1. 在代码中添加日志记录`__file__`的值
2. 使用`--file-reference-choice=original`保持原始路径
3. 或者使用`--file-reference-choice=runtime`让程序使用运行时位置
4. 在代码中使用`sys.executable`获取可执行文件路径

### 6.5 内存问题调试
对于内存相关问题：
1. 使用`--unstripped`保留调试符号
2. 考虑使用`--low-memory`选项减少编译时内存使用
3. 检查大型数据结构的使用和释放
4. 对于Python对象引用问题，可以在代码中添加引用计数检查

### 6.6 DLL依赖问题
对于DLL加载问题：
1. 使用`--report`生成依赖报告
2. 检查`QCstt_deps_report.xml`文件中的DLL依赖
3. 使用`--list-package-dlls=包名`查看特定包的DLL
4. 确保所有必要的DLL都被正确包含
