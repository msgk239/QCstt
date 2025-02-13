# Joblib Windows系统CPU核心数获取问题修复指南

## 问题描述

在Windows系统上使用joblib时，可能会遇到与CPU核心数获取相关的错误。这是因为joblib使用了已经过时的`wmic`命令来获取CPU信息。

## 解决方案

需要修改joblib的源代码文件：`.conda\Lib\site-packages\joblib\externals\loky\backend\context.py`

将原有的使用`wmic`的代码段替换为使用PowerShell命令的新实现：

```python
elif sys.platform == "win32":
    cpu_info = subprocess.run(
        ["powershell", "Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty NumberOfCores"],
        capture_output=True,
        text=True
    )
    cpu_count_physical = int(cpu_info.stdout.strip())
```

## 原因说明

1. `wmic`命令在较新版本的Windows系统中已被弃用
2. 新的实现使用PowerShell的`Get-CimInstance`命令，这是获取系统硬件信息的推荐方式
3. 该命令可以准确获取CPU的物理核心数

## 注意事项

1. 修改第三方库源代码后，如果更新库可能会覆盖修改，需要重新应用此修复
2. 确保系统中已安装PowerShell（Windows 10及以上版本默认已安装）
3. 执行PowerShell命令需要适当的系统权限

## 验证方法

### 方法1：直接在PowerShell中验证
在PowerShell或Windows终端中直接运行以下命令：
```powershell
Get-CimInstance -ClassName Win32_Processor | Select-Object -ExpandProperty NumberOfCores
```
如果命令返回一个数字（例如：8），说明命令可以正常工作。

### 方法2：在Python中验证
修改完成后，可以通过以下Python代码验证是否能正确获取CPU核心数：

```python
from joblib import parallel_backend
from joblib import Parallel, delayed

# 尝试执行一个简单的并行任务
with parallel_backend('loky'):
    results = Parallel(n_jobs=2)(delayed(lambda x: x * x)(i) for i in range(10))
```

如果代码正常执行，说明修复成功。 