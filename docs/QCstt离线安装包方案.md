# QCstt 离线安装包方案

## 方案概述

为潜催语音转文字系统(QCstt)创建一个完整的离线安装包，包含所有必要组件和依赖，并使用专业安装器提供用户友好的安装体验。

## 技术架构

1. **核心组件**
   - Nuitka编译的应用代码（非standalone模式）
   - Miniconda安装程序
   - 预下载的Conda和pip依赖包
   - 自定义安装脚本和启动脚本

2. **压缩与打包**
   - 使用7-Zip高压缩率压缩依赖包
   - 使用Inno Setup创建Windows安装程序
   - 为其他平台提供对应安装方式

## 安装包结构

```
QCstt-Installer/
├── app/                    # 应用程序文件
│   ├── bin/                # 编译后的二进制文件
│   ├── server/             # 服务器代码
│   └── frontend/           # 前端文件
├── packages/               # 预下载的依赖包
│   ├── conda-pkgs/         # Conda包
│   └── pip-pkgs/           # pip包
├── miniconda/              # Miniconda安装程序
├── scripts/                # 安装和配置脚本
└── [安装程序文件]           # 最终生成的安装程序
```

## 安装流程

1. **用户启动安装程序**
2. **选择安装选项**
   - 安装位置
   - 开始菜单/桌面快捷方式
   - 安装类型（完整/最小）
3. **安装过程**
   - 解压应用文件
   - 安装Miniconda（如果未安装）
   - 创建Conda环境
   - 从本地源安装依赖
   - 配置环境变量和启动脚本
4. **完成安装**
   - 创建快捷方式
   - 显示安装完成信息

## 维护与更新

1. **版本更新流程**
   - 更新应用代码并重新编译
   - 更新environment.yml文件
   - 下载新增或更新的依赖包
   - 重新生成安装程序

2. **补丁更新**
   - 可创建仅包含更新部分的小型补丁包
   - 补丁安装器检测现有安装并更新

## 技术实现细节

1. **依赖包准备**
   ```bash
   # 下载Conda依赖
   conda create -n temp_env --file environment.yml --dry-run
   conda list --explicit > explicit_deps.txt
   conda download --file explicit_deps.txt -p ./conda-pkgs
   
   # 下载pip依赖
   pip download -r requirements.txt -d ./pip-pkgs
   
   # 压缩包
   7z a -t7z -mx=9 -ms=on packages.7z conda-pkgs/ pip-pkgs/
   ```

2. **安装器创建**
   - 使用Inno Setup脚本定义安装流程
   - 包含解压、安装和配置步骤
   - 添加进度显示和错误处理

3. **多平台支持**
   - Windows: Inno Setup (.exe)
   - macOS: DMG或pkg安装包
   - Linux: 自解压脚本或deb/rpm包

## 优势与限制

**优势:**
- 完全离线安装，无需网络连接
- 专业的安装体验
- 确保依赖版本一致性
- 减少安装失败的可能性

**限制:**
- 安装包体积较大（即使压缩后）
- 需要为不同平台创建不同安装包
- 更新维护需要重新打包

## 未来改进方向

1. **增量更新系统**
   - 实现只下载和安装变更部分的机制

2. **组件化安装**
   - 允许用户选择安装特定功能模块

3. **自动更新检测**
   - 添加检查和提示更新的功能

4. **安装遥测**
   - 收集安装成功率和错误信息（可选且匿名）
