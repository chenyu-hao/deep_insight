@echo off
chcp 65001 >nul

REM Windows 批量登录环境启动脚本

set PLATFORM=%1
if "%PLATFORM%"=="" set PLATFORM=xhs

REM 验证平台参数
set VALID=0
for %%p in (xhs dy ks wb bili tieba zhihu) do (
    if "%PLATFORM%"=="%%p" set VALID=1
)

if "%VALID%"=="0" (
    echo [ERROR] 不支持的平台: %PLATFORM%
    echo 用法: %~nx0 [xhs^|dy^|ks^|wb^|bili^|tieba^|zhihu]
    pause
    exit /b 1
)

REM 创建必要目录
if not exist "browser_data" mkdir browser_data
if not exist "runtime" mkdir runtime

REM 初始化 cookies.json
if not exist "runtime\cookies.json" (
    echo {} > runtime\cookies.json
)

echo ================================================
echo   正在启动 %PLATFORM% 登录环境...
echo ================================================
echo.

REM 设置环境变量并启动 Docker
set LOGIN_PLATFORM=%PLATFORM%
docker compose --profile login up -d --build crawler-login

echo.
echo 登录说明:
echo 1. 请在浏览器打开: http://localhost:6080/vnc.html
echo 2. 在 VNC 桌面中完成扫码登录
echo 3. 登录成功后，运行以下命令停止登录容器:
echo    docker compose --profile login stop crawler-login
echo.
echo 登录态将保存在:
echo - ./browser_data
echo - ./runtime/cookies.json
echo.
pause