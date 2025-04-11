@echo off
REM 激活虚拟环境
call conda activate ./.conda

REM 启动 Python 服务
python -m server.api.package
pause