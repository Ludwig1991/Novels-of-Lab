@echo off
chcp 65001 >nul
title 知识库AI系统 V2

echo ========================================
echo    知识库AI系统 V2 - 全自动版
echo ========================================
echo.
echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    pause
    exit /b 1
)
echo ✓ Python 已安装

echo.
echo [2/4] 检查依赖包...
pip show flask flask-cors anthropic >nul 2>&1
if errorlevel 1 (
    echo 正在安装依赖...
    pip install flask flask-cors anthropic
)
echo ✓ 依赖已就绪

echo.
echo [3/4] 启动 AI Client (端口 5000)...
start "AI Client V2" cmd /k "cd /d F:\雾月督政府\上层 && python ai_knowledge_client_v2.py"
echo ✓ AI Client 已启动

timeout /t 3 /nobreak >nul

echo.
echo [4/4] 打开前端界面...
start "" "F:\雾月督政府\上层\ai_knowledge_client_v2.html"

echo.
echo ========================================
echo ✅ 系统启动完成!
echo.
echo 使用说明:
echo   1. 前端界面已自动打开
echo   2. 在 "生成卡片" 标签页输入主题
echo   3. 可选择源文件或直接输入主题
echo   4. 点击 "一键生成并发送"
echo   5. 监听器自动处理并写入记忆库
echo.
echo ⚠️ 注意: 记得先启动 watcher_service.py
echo ========================================
echo.
pause