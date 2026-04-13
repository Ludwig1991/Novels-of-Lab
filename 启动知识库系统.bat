@echo off
chcp 65001 >nul
title 知识库AI系统启动器

echo ========================================
echo    知识库AI客户端 V2 启动器
echo ========================================
echo.

echo [1/3] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    pause
    exit /b 1
)
echo ✓ Python 已安装

echo.
echo [2/3] 检查依赖包...
pip show flask flask-cors anthropic >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install flask flask-cors anthropic watchdog jinja2
)
echo ✓ 依赖已就绪

echo.
echo [3/3] 启动服务...
echo.
echo 启动顺序:
echo   1. AI Client (端口 5000)
echo   2. 前端界面 (浏览器打开)
echo.
echo 启动前确保 watcher_service.py 已运行!
echo.

start "AI Client V2" cmd /k "python ai_knowledge_client_v2.py"

timeout /t 2 /nobreak >nul

start "" "ai_knowledge_client_v2.html"

echo.
echo ========================================
echo 服务已启动!
echo   - 前端界面: ai_knowledge_client_v2.html
echo   - 后端API: http://localhost:5000
echo ========================================
echo.
echo 接下来请确保 watcher_service.py 正在运行
echo 然后在浏览器中使用前端界面
echo.
pause
