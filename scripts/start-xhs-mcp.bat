@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM 小红书 MCP 服务启动脚本

title 小红书 MCP 服务

REM 初始化 fnm (如果存在)
where fnm >nul 2>&1
if %errorlevel% equ 0 (
    FOR /f "tokens=*" %%z IN ('fnm env --use-on-cd') DO CALL %%z
)

echo ================================================
echo   小红书 MCP 服务
echo ================================================
echo.

set XHS_DIR=external\XHS-MCP\xiaohongshu-mcp-windows-amd64
set XHS_MCP=%XHS_DIR%\xiaohongshu-mcp-windows-amd64.exe
set XHS_LOGIN=%XHS_DIR%\xiaohongshu-login-windows-amd64.exe

REM 检查文件是否存在
if not exist "%XHS_MCP%" (
    echo [ERROR] 未找到 MCP 服务文件
    echo 请先运行主启动脚本: start.bat
    pause
    exit /b 1
)

REM 检查登录状态
echo [INFO] 检查登录状态...
if exist "%XHS_DIR%\cookies.json" (
    findstr /C:"web_session" "%XHS_DIR%\cookies.json" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SUCCESS] 登录状态有效 ✓
    ) else (
        goto :login_prompt
    )
) else (
    :login_prompt
    echo [WARNING] 未找到有效的登录信息
    echo 小红书发布功能将不可用
    echo.
    set /p LOGIN_NOW="是否现在登录？(y/n): "
    if /i "!LOGIN_NOW!"=="y" (
        echo [INFO] 启动登录工具...
        echo 请在弹出的浏览器窗口中扫码登录
        echo.
        cd "%XHS_DIR%"
        start /wait xiaohongshu-login-windows-amd64.exe
        cd ..\..\..
        if exist "%XHS_DIR%\cookies.json" (
            echo [SUCCESS] 登录成功 ✓
        ) else (
            echo [WARNING] 登录失败或已取消
            echo 稍后可手动运行: cd %XHS_DIR% ^&^& xiaohongshu-login-windows-amd64.exe
            echo.
            pause
        )
    ) else (
        echo [WARNING] 跳过登录，服务将启动但发布功能不可用
        echo 稍后可手动运行: cd %XHS_DIR% ^&^& xiaohongshu-login-windows-amd64.exe
        echo.
        pause
    )
)

echo.
echo [INFO] 启动小红书 MCP 服务...
echo 端口: 18060
echo 验证: curl http://localhost:18060/mcp
echo.
echo [提示] 按 Ctrl+C 停止服务
echo.

REM 进入目录并启动服务
cd "%XHS_DIR%"
xiaohongshu-mcp-windows-amd64.exe
