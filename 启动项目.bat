@echo off
REM ========================================
REM AI 测试用例生成系统 - 快速启动脚本
REM Windows 一键部署脚本
REM ========================================

echo ========================================
echo   AI 测试用例生成系统 - 快速启动
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python,请先安装 Python 3.12+
    pause
    exit /b 1
)

echo [1/5] 检查虚拟环境...
if not exist "testbrain-venv" (
    echo 创建虚拟环境...
    python -m venv testbrain-venv
    echo 虚拟环境创建成功!
) else (
    echo 虚拟环境已存在
)

echo.
echo [2/5] 激活虚拟环境...
call testbrain-venv\Scripts\activate.bat

echo.
echo [3/5] 安装依赖包...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [警告] 依赖安装可能有问题,请检查错误信息
) else (
    echo 依赖安装完成!
)

echo.
echo [4/5] 检查数据库配置...
if not exist ".env" (
    echo [错误] .env 文件不存在,请先配置环境变量
    pause
    exit /b 1
)
echo 环境配置文件已找到

echo.
echo [5/5] 执行数据库迁移...
python manage.py makemigrations --noinput
python manage.py migrate --noinput
if %errorlevel% neq 0 (
    echo [警告] 数据库迁移失败,请检查 MySQL 配置
) else (
    echo 数据库迁移完成!
)

echo.
echo ========================================
echo   启动成功! 正在启动服务器...
echo ========================================
echo.
echo 访问地址: http://127.0.0.1:9002
echo 按 Ctrl+C 停止服务器
echo.

python main.py
