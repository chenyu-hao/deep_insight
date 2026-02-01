@echo off
chcp 65001 >nul

REM 前端服务启动脚本

title 前端开发服务器 (Vue 3 + Vite)

REM 初始化 fnm (如果存在)
where fnm >nul 2>&1
if %errorlevel% equ 0 (
    FOR /f "tokens=*" %%z IN ('fnm env --use-on-cd') DO CALL %%z
)

echo ================================================
echo   前端开发服务器 (Vue 3 + Vite)
echo ================================================
echo.

REM 检查 node_modules
if not exist "node_modules" (
    echo [ERROR] node_modules 不存在
    echo 请先运行主启动脚本: start.bat
    pause
    exit /b 1
)

echo [INFO] 启动前端开发服务器...
echo 端口: 5173
echo 访问: http://localhost:5173
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.

REM 启动服务
call npm run dev
