@echo off
chcp 65001 >nul

REM 后端服务启动脚本

title 后端 API 服务 (FastAPI)

REM 初始化 fnm (如果存在)
where fnm >nul 2>&1
if %errorlevel% equ 0 (
    FOR /f "tokens=*" %%z IN ('fnm env --use-on-cd') DO CALL %%z
)

echo ================================================
echo   后端 API 服务 (FastAPI)
echo ================================================
echo.

REM 检查虚拟环境
set VENV_DIR=
if exist ".venv" (
    set VENV_DIR=.venv
) else if exist "..\venv" (
    set VENV_DIR=..\venv
) else if exist "..\.venv" (
    set VENV_DIR=..\.venv
)
if "%VENV_DIR%"=="" (
    echo [ERROR] 虚拟环境不存在
    echo 请先运行主启动脚本: start.bat
    pause
    exit /b 1
)

echo [INFO] 激活虚拟环境...
call %VENV_DIR%\Scripts\activate.bat

REM 检查环境变量
if not exist ".env" (
    echo [WARNING] .env 文件不存在
    echo 将使用默认配置，部分功能可能不可用
    echo.
)

echo [INFO] 启动后端服务...
echo 端口: 8000
echo API 文档: http://localhost:8000/docs
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.

REM 启动服务
python -m app.main
