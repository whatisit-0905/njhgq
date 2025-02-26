@echo off
:: 显示当前步骤
echo Initializing...

:: 设置编码为 UTF-8
chcp 65001

:: 设置 Conda 路径
set CONDA_PATH=C:\ProgramData\miniconda3

:: 初始化 conda
echo Initializing Conda...
call %CONDA_PATH%\Scripts\activate.bat

:: 激活环境
echo Activating py38 environment...
call conda activate py39

:: 验证 Python 环境
echo Checking Python environment...
python --version


:: 切换到项目目录并启动后端
echo Starting backend service...
cd /d D:\nanjing1
"D:\anaconda3\envs\py39\python.exe" main.py

:: 暂停以查看输出
pause
