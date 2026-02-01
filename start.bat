@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM GlobalInSight 快速启动脚本
REM 适用于 Windows 系统

title GlobalInSight 启动脚本

echo ================================================
echo   GlobalInSight 快速启动脚本
echo   Multi-Stage Public Opinion Interpretation
echo ================================================
echo.

REM 检查 Python
echo [INFO] 检查 Python 环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.9+
    echo [INFO] 下载地址: https://www.python.org/downloads/
    echo [INFO] 安装时请勾选 "Add Python to PATH"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [SUCCESS] Python 版本: %PYTHON_VERSION% ✓
echo.

REM 初始化 fnm (如果存在)
where fnm >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] 检测到 fnm，正在初始化...
    FOR /f "tokens=*" %%z IN ('fnm env --use-on-cd') DO CALL %%z
)

REM 检查 Node.js
echo [INFO] 检查 Node.js 环境...
where node >nul 2>&1
if %errorlevel% neq 0 (
    node --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] 未找到 Node.js，请先安装 Node.js 16+
        echo [INFO] 下载地址: https://nodejs.org/
        echo [INFO] 或使用 fnm: fnm install --lts
        pause
        exit /b 1
    )
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo [SUCCESS] Node.js 版本: %NODE_VERSION% ✓
echo.

REM 设置虚拟环境
echo [INFO] 设置 Python 虚拟环境...
if not exist ".venv" (
    echo [INFO] 创建虚拟环境...
    python -m venv .venv
)
echo [SUCCESS] 虚拟环境已就绪 ✓
echo.

REM 检查环境变量
echo [INFO] 检查环境变量配置...
if not exist ".env" (
    echo [WARNING] .env 文件不存在，从 .env.example 复制...
    copy .env.example .env >nul
    echo [WARNING] 请编辑 .env 文件，填入你的 API Keys
    echo [INFO] 至少需要配置一个 LLM 提供商的 API Key
) else (
    echo [SUCCESS] 环境变量配置文件存在 ✓
)
echo.

REM 安装 Python 依赖
echo [INFO] 检查 Python 依赖...
call .venv\Scripts\activate.bat

python -c "import fastapi" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] 安装 Python 依赖（首次运行可能需要几分钟）...
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q
    echo [SUCCESS] Python 依赖安装完成 ✓
) else (
    echo [SUCCESS] Python 依赖已安装 ✓
)
echo.

REM 检查 Playwright
python -c "from playwright.sync_api import sync_playwright" 2>nul
if %errorlevel% neq 0 (
    echo [INFO] 安装 Playwright 浏览器...
    playwright install chromium
    echo [SUCCESS] Playwright 安装完成 ✓
    echo.
)

REM 安装 Node.js 依赖
echo [INFO] 检查 Node.js 依赖...
if not exist "node_modules" (
    echo [INFO] 安装 Node.js 依赖（首次运行可能需要几分钟）...
    call npm install
    echo [SUCCESS] Node.js 依赖安装完成 ✓
) else (
    echo [SUCCESS] Node.js 依赖已安装 ✓
)
echo.

REM 设置小红书 MCP
echo [INFO] 检查小红书 MCP 服务...
set XHS_DIR=XHS-MCP\xiaohongshu-mcp-windows-amd64
set XHS_MCP=%XHS_DIR%\xiaohongshu-mcp-windows-amd64.exe
set XHS_LOGIN=%XHS_DIR%\xiaohongshu-login-windows-amd64.exe

if not exist "%XHS_DIR%" mkdir "%XHS_DIR%"

if not exist "%XHS_MCP%" (
    echo [WARNING] 未找到小红书 MCP 服务，正在下载...
    curl -L -o "%XHS_MCP%" "https://github.com/xpzouying/xiaohongshu-mcp/releases/latest/download/xiaohongshu-mcp-windows-amd64.exe"
    curl -L -o "%XHS_LOGIN%" "https://github.com/xpzouying/xiaohongshu-mcp/releases/latest/download/xiaohongshu-login-windows-amd64.exe"
    echo [SUCCESS] 小红书 MCP 服务下载完成 ✓
) else (
    echo [SUCCESS] 小红书 MCP 服务已存在 ✓
)
echo.

REM 检查登录状态
echo [INFO] 检查小红书登录状态...
if exist "%XHS_DIR%\cookies.json" (
    findstr /C:"web_session" "%XHS_DIR%\cookies.json" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [SUCCESS] 小红书登录状态有效 ✓
    ) else (
        goto :xhs_login_prompt
    )
) else (
    :xhs_login_prompt
    echo [WARNING] 未找到有效的小红书登录信息
    echo [INFO] 首次使用需要登录小红书（用于发布功能）
    echo.
    set /p LOGIN_CHOICE="是否现在登录？(y/n，直接回车跳过): "
    if /i "!LOGIN_CHOICE!"=="y" (
        echo.
        echo [INFO] 启动小红书登录工具...
        echo [INFO] 请在弹出的浏览器窗口中：
        echo [INFO]   1. 使用小红书 APP 扫描二维码
        echo [INFO]   2. 确认登录
        echo [INFO]   3. 等待浏览器自动关闭
        echo.
        echo [提示] 如果浏览器没有弹出，请手动运行：
        echo [提示] cd %XHS_DIR% ^&^& xiaohongshu-login-windows-amd64.exe
        echo.
        pause
        cd "%XHS_DIR%"
        xiaohongshu-login-windows-amd64.exe
        cd ..\..
        echo.
        if exist "%XHS_DIR%\cookies.json" (
            echo [SUCCESS] 登录完成，可以使用小红书发布功能 ✓
        ) else (
            echo [WARNING] 未检测到登录信息
            echo [INFO] 可能原因：
            echo [INFO]   - 未完成扫码登录
            echo [INFO]   - 登录工具启动失败
            echo [INFO]   - 浏览器被阻止弹出
            echo.
            echo [INFO] 稍后可手动登录：
            echo [INFO] cd %XHS_DIR% ^&^& xiaohongshu-login-windows-amd64.exe
        )
    ) else (
        echo [INFO] 跳过登录，小红书发布功能将不可用
        echo [INFO] 稍后可手动登录：
        echo [INFO] cd %XHS_DIR% ^&^& xiaohongshu-login-windows-amd64.exe
    )
)
echo.

echo [SUCCESS] 环境检查完成！
echo.
echo [INFO] 准备启动服务...
echo.

REM 询问是否启动 Opinion MCP
set /p START_OPINION="是否启动 Opinion MCP 服务（用于 ClawdBot 集成）？(y/n): "
echo.

if /i "%START_OPINION%"=="y" (
    echo [INFO] 将在 4 个新命令行窗口中启动服务：
    echo [INFO]   1. 小红书 MCP 服务 ^(端口 18060^)
    echo [INFO]   2. 后端 API 服务 ^(端口 8000^)
    echo [INFO]   3. 前端开发服务器 ^(端口 5173^)
    echo [INFO]   4. Opinion MCP 服务 ^(端口 18061^)
) else (
    echo [INFO] 将在 3 个新命令行窗口中启动服务：
    echo [INFO]   1. 小红书 MCP 服务 ^(端口 18060^)
    echo [INFO]   2. 后端 API 服务 ^(端口 8000^)
    echo [INFO]   3. 前端开发服务器 ^(端口 5173^)
)
echo.
pause

REM 获取当前目录
set CURRENT_DIR=%CD%

REM 启动小红书 MCP 服务
start "小红书 MCP 服务" cmd /k "cd /d "%CURRENT_DIR%" && scripts\start-xhs-mcp.bat"
timeout /t 2 /nobreak >nul

REM 启动后端服务
start "后端 API 服务" cmd /k "cd /d "%CURRENT_DIR%" && scripts\start-backend.bat"
timeout /t 2 /nobreak >nul

REM 启动前端服务
start "前端开发服务器" cmd /k "cd /d "%CURRENT_DIR%" && scripts\start-frontend.bat"

REM 启动 Opinion MCP 服务（如果用户选择）
if /i "%START_OPINION%"=="y" (
    timeout /t 2 /nobreak >nul
    start "Opinion MCP 服务" cmd /k "cd /d "%CURRENT_DIR%" && scripts\start-opinion-mcp.bat"
)

echo.
echo [SUCCESS] 所有服务已在新窗口中启动！
echo.
echo [INFO] 服务地址：
echo [INFO]   • 前端: http://localhost:5173
echo [INFO]   • 后端 API: http://localhost:8000
echo [INFO]   • API 文档: http://localhost:8000/docs
echo [INFO]   • 小红书 MCP: http://localhost:18060/mcp
if /i "%START_OPINION%"=="y" (
    echo [INFO]   • Opinion MCP: http://localhost:18061/health
)
echo.
echo [INFO] 首次使用请访问前端设置页面配置 API Keys
if /i "%START_OPINION%"=="y" (
    echo [INFO] Opinion MCP 可用于 ClawdBot 集成，详见 README.md
)
echo.
pause
