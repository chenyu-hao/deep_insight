@echo off
chcp 65001 >nul

REM Opinion MCP 服务启动脚本

title Opinion MCP 服务

REM 初始化 fnm (如果存在)
where fnm >nul 2>&1
if %errorlevel% equ 0 (
    FOR /f "tokens=*" %%z IN ('fnm env --use-on-cd') DO CALL %%z
)

echo ================================================
echo   Opinion MCP 服务 (ClawdBot 集成)
echo ================================================
echo.

REM 检查虚拟环境
if not exist ".venv" (
    echo [ERROR] 虚拟环境不存在
    echo 请先运行主启动脚本: start.bat
    pause
    exit /b 1
)

echo [INFO] 激活虚拟环境...
call .venv\Scripts\activate.bat

REM 检查环境变量
if not exist ".env" (
    echo [WARNING] .env 文件不存在
    echo 将使用默认配置，部分功能可能不可用
    echo.
)

echo [INFO] 启动 Opinion MCP 服务...
echo 端口: 18061
echo 健康检查: http://localhost:18061/health
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.

REM 启动服务
python -m app.services.opinion_mcp_server
